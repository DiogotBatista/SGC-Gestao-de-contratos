from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tarefa(models.Model):
    descricao = models.CharField("Descrição", max_length=255)
    concluida = models.BooleanField("Concluída", default=False)
    criada_em = models.DateTimeField("Criada em", auto_now_add=True)
    autor = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ["-criada_em"]
        verbose_name = "Tarefa"
        verbose_name_plural = "Tarefas"

    def __str__(self):
        return self.descricao
