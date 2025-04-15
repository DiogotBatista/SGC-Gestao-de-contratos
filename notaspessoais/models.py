from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class NotaPessoal(models.Model):
    titulo = models.CharField(max_length=200, verbose_name="Título")
    texto = models.TextField(verbose_name="Texto da anotação")
    criada_em = models.DateTimeField(auto_now_add=True, verbose_name="Criada em")
    atualizada_em = models.DateTimeField(auto_now=True, verbose_name="Atualizada em")
    autor = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Autor")

    class Meta:
        verbose_name = "Nota Pessoal"
        verbose_name_plural = "Notas Pessoais"
        ordering = ['-criada_em']

    def __str__(self):
        return self.titulo
