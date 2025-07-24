import random
import string
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


# Modelo para la tabla CIUDAD
class Ciudad(models.Model):
    ciudad_id = models.AutoField(primary_key=True)
    ciudad = models.CharField(choices=(
        ('Asunción', 'Asunción'),
        ('San Lorenzo', 'San Lorenzo'),
        ('Capiatá', 'Capiatá'),
        ('Lambaré', 'Lambaré'),
        ('Fernando de la Mora', 'Fernando de la Mora'),
        ('Luque', 'Luque'),
        ('Mariano Roque Alonso', 'Mariano Roque Alonso'),
        ('Limpio', 'Limpio'),
        ('Ñemby', 'Ñemby'),
        ('Itauguá', 'Itauguá'),
        ('Villa Elisa', 'Villa Elisa'),
        ('San Antonio', 'San Antonio'),
        ('Villa Hayes', 'Villa Hayes'),
        ('San Juan Bautista', 'San Juan Bautista'),
        ('Encarnación', 'Encarnación'),
        ('Ciudad del Este', 'Ciudad del Este'),
        ('Hernandarias', 'Hernandarias'),
        ('Presidente Franco', 'Presidente Franco'),
        ('CDE (Mcal. Estigarribia)', 'CDE (Mcal. Estigarribia)'),
        ('Caaguazú', 'Caaguazú'),
        ('Coronel Oviedo', 'Coronel Oviedo'),
        ('Villarrica', 'Villarrica'),
        ('Pilar', 'Pilar'),
        ('Caazapá', 'Caazapá'),
        ('Caacupé', 'Caacupé'),
        ('San Juan Nepomuceno', 'San Juan Nepomuceno'),
        ('Paraguarí', 'Paraguarí'),
        ('Areguá', 'Areguá'),
        ('Ypacaraí', 'Ypacaraí'),
        ('Pirayú', 'Pirayú'),
        ('Jesús', 'Jesús'),
        ('San Bernardino', 'San Bernardino'),
        ('Altos', 'Altos'),
        ('Ypané', 'Ypané'),
        ('Yaguaron', 'Yaguaron'),
        ('Tobatí', 'Tobatí'),
        ('Carapeguá', 'Carapeguá'),
        ('Nueva Colombia', 'Nueva Colombia'),
        ('Villa Rica', 'Villa Rica'),
        ('Arroyos y Esteros', 'Arroyos y Esteros'),
        ('San Estanislao', 'San Estanislao'),
        ('Horqueta', 'Horqueta'),
        ('Concepción', 'Concepción'),
        ('San Lázaro', 'San Lázaro'),
        ('Loma Grande', 'Loma Grande'),
        ('Santa Rosa del Aguaray', 'Santa Rosa del Aguaray'),
        ('Curuguaty', 'Curuguaty'),
        ('Villa del Rosario', 'Villa del Rosario'),
        ('Bella Vista', 'Bella Vista'),
        ('Pedro Juan Caballero', 'Pedro Juan Caballero'),
        ('Salto del Guairá', 'Salto del Guairá'),
        ('Doctor Juan León Mallorquín', 'Doctor Juan León Mallorquín'),
        ('Hohenau', 'Hohenau'),
        ('Buenos Aires', 'Buenos Aires'),
        ('Santa Rita', 'Santa Rita'),
        ('Nueva Esperanza', 'Nueva Esperanza'),
        ('Pozo Colorado', 'Pozo Colorado'),
        ('José Falcón', 'José Falcón'),
        ('La Victoria', 'La Victoria'),
        ('Mariscal Estigarribia', 'Mariscal Estigarribia'),
        ('Villa Oliva', 'Villa Oliva'),
        ('Humaitá', 'Humaitá'),
        ('Ayolas', 'Ayolas'),
        ('San Cosme y Damián', 'San Cosme y Damián'),
        ('General Delgado', 'General Delgado'),
        ('Itá', 'Itá'),
        ('Piribebuy', 'Piribebuy'),
        ('Guarambaré', 'Guarambaré'),
        ('Villeta', 'Villeta'),
        ('Nueva Italia', 'Nueva Italia'),
        ('Ypane', 'Ypane'),
    ), unique=True)

    departamento = models.CharField(choices=(
        ('Alto Paraguay', 'Alto Paraguay'),
        ('Alto Paraná', 'Alto Paraná'),
        ('Amambay', 'Amambay'),
        ('Boquerón', 'Boquerón'),
        ('Caaguazú', 'Caaguazú'),
        ('Caazapá', 'Caazapá'),
        ('Canindeyú', 'Canindeyú'),
        ('Central', 'Central'),
        ('Concepción', 'Concepción'),
        ('Guairá', 'Guairá'),
        ('Itapúa', 'Itapúa'),
        ('Cordillera', 'Cordillera'),
        ('Misiones', 'Misiones'),
        ('Ñeembucú', 'Ñeembucú'),
        ('Paraguarí', 'Paraguarí'),
        ('Presidente Hayes', 'Presidente Hayes'),
        ('San Pedro', 'San Pedro'),
    ))
    postal_code = models.IntegerField()

    def __str__(self):
        return f"{self.ciudad} - {self.departamento}"

class PersonaManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El campo "email" es obligatorio.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

# Modelo de usuario normal (Persona)
class Persona(AbstractBaseUser, PermissionsMixin):
    persona_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    ciudad_id = models.ForeignKey(Ciudad, on_delete=models.CASCADE, null=True)
    nombre = models.CharField(max_length=255)
    apellido = models.CharField(max_length=255)
    tipo_documento = models.CharField(choices=(
        ('Pasaporte', 'Pasaporte'),
        ('RUC', 'RUC'),
        ('CI', 'CI'),
    ), default='CI')
    numero_documento = models.CharField(max_length=255, unique=True)
    direccion = models.CharField(max_length=255)
    celular = models.CharField(max_length=255)
    estado = models.CharField(choices=(
        ('Activo', 'Activo'),
        ('Inactivo', 'Inactivo'),
        ('Bloqueado', 'Bloqueado'),
        ('Cerrado', 'Cerrado'),
        ('Pendiente', 'Pendiente'),
        ('Suspendido', 'Suspendido'),
        ('En revisión', 'En revisión'),
    ), default='Activo')
    custom_username = models.CharField(max_length=30, unique=True, null=True, blank=True)
    objects = PersonaManager()

    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        related_name='user_personas'  # Cambia 'user_personas' a un nombre único
    )

    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        related_name='user_personas_permissions'  # Cambia 'user_personas_permissions' a un nombre único
    )

    USERNAME_FIELD = 'custom_username'
    REQUIRED_FIELDS = ['email', 'nombre', 'apellido', 'numero_documento']

    is_staff = models.BooleanField(default=False)

    def __str__(self):
        return self.custom_username

    def save(self, *args, **kwargs):
        if not self.custom_username:
            # Genera el username a partir de la primera letra del nombre y número de documento
            self.custom_username = f"{self.nombre[0]}{self.numero_documento}"
        super().save(*args, **kwargs)

@receiver(post_save, sender=Persona)
def crear_cliente(sender, instance, created, **kwargs):
    if created:
        # Verifica si se ha creado una nueva instancia de Persona
        Cliente.objects.create(persona_id=instance,
                               calificacion='Sin Calificacion',
                               estado='Activo')


# Modelo para la tabla CLIENTE
class Cliente(models.Model):
    cliente_id = models.AutoField(primary_key=True)
    persona_id = models.OneToOneField(Persona, on_delete=models.CASCADE)
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    calificacion = models.CharField(choices=(
        ('Excelente', 'Excelente'),
        ('Bueno', 'Bueno'),
        ('Regular', 'Regular'),
        ('Malo', 'Malo'),
        ('Sin calificación', 'Sin calificación'),
    ))
    estado = models.CharField(choices=(
        ('Activo', 'Activo'),
        ('Inactivo', 'Inactivo'),
        ('Bloqueado', 'Bloqueado'),
        ('Cerrado', 'Cerrado'),
        ('En revisión', 'En revisión'),
        ('Suspendido', 'Suspendido'),
    ))

    def __str__(self):
        return f"{self.persona_id}"