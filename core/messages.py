# core/messages.py
from django.contrib import messages
from django.utils.text import capfirst

# ===== Helpers genéricos ======================================================


def _model_verbose_name(obj_or_model):
    """
    Retorna o verbose_name do model, capitalizado.
    Aceita a classe do model OU uma instância.
    """
    model = obj_or_model if hasattr(obj_or_model, "_meta") else obj_or_model.__class__
    return capfirst(model._meta.verbose_name)


def _obj_display(obj):
    """
    Como exibir o objeto na mensagem. Se __str__ for útil, usa; senão só o verbose_name.
    """
    try:
        text = str(obj).strip()
        if text and text != object.__str__(obj):
            return text
    except Exception:
        pass
    return _model_verbose_name(obj)


def add_created_message(request, obj, extra_text: str | None = None):
    name = _obj_display(obj)
    suffix = f" {extra_text.strip()}" if extra_text else ""
    messages.success(request, f"{name} cadastrado com sucesso!{suffix}")


def add_updated_message(request, obj, extra_text: str | None = None):
    name = _obj_display(obj)
    suffix = f" {extra_text.strip()}" if extra_text else ""
    messages.info(request, f"{name} atualizado com sucesso!{suffix}")


def add_deleted_message(request, model_or_obj, extra_text: str | None = None):
    name = _model_verbose_name(model_or_obj)
    suffix = f" {extra_text.strip()}" if extra_text else ""
    messages.warning(request, f"{name} excluído com sucesso!{suffix}")


def add_error_message(request, text: str = "Erro ao processar a ação."):
    messages.error(request, text)


# ===== Mixins para Class-Based Views =========================================
# Use em conjunto com CreateView, UpdateView e DeleteView.


class CreatedMessageMixin:
    """
    Para CreateView: adiciona messages.success no form_valid
    """

    created_message_extra: str | None = None  # opcional

    def form_valid(self, form):
        response = super().form_valid(form)
        add_created_message(self.request, self.object, self.created_message_extra)
        return response


class UpdatedMessageMixin:
    """
    Para UpdateView: adiciona messages.info no form_valid
    """

    updated_message_extra: str | None = None  # opcional

    def form_valid(self, form):
        response = super().form_valid(form)
        add_updated_message(self.request, self.object, self.updated_message_extra)
        return response


class DeletedMessageMixin:
    """
    Para DeleteView: adiciona messages.warning no delete
    """

    deleted_message_extra: str | None = None  # opcional

    def delete(self, request, *args, **kwargs):
        # guarde o model antes porque super().delete remove a instância
        self.object = self.get_object()
        model_for_name = self.object.__class__
        response = super().delete(request, *args, **kwargs)
        add_deleted_message(request, model_for_name, self.deleted_message_extra)
        return response


# ===== Atalhos para Function-Based Views =====================================


def message_created_ok(request, obj, extra_text: str | None = None):
    add_created_message(request, obj, extra_text)


def message_updated_ok(request, obj, extra_text: str | None = None):
    add_updated_message(request, obj, extra_text)


def message_deleted_ok(request, model_or_obj, extra_text: str | None = None):
    add_deleted_message(request, model_or_obj, extra_text)


def message_error(request, text: str = "Erro ao processar a ação."):
    add_error_message(request, text)
