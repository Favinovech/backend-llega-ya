from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import (
    Usuario, Rol, Negocio, Producto, Pedido, DetallePedido,
    HistorialCambioProducto, HistorialEstadoPedido,
)

class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Rol
        fields = ['id', 'nombre']


class UsuarioSerializer(serializers.ModelSerializer):
    rol = RolSerializer(read_only=True)

    class Meta:
        model  = Usuario
        fields = ['id', 'email', 'nombre', 'apellido', 'telefono', 'rol', 'activo', 'created_at', 'foto']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    rol_id   = serializers.PrimaryKeyRelatedField(
        queryset=Rol.objects.all(), source='rol', write_only=True, required=False
    )

    class Meta:
        model  = Usuario
        fields = ['email', 'nombre', 'apellido', 'telefono', 'password', 'rol_id']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = Usuario(**validated_data)
        user.set_password(password)
        user.save()
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email']  = user.email
        token['nombre'] = user.nombre
        token['rol']    = user.rol.nombre if user.rol else None
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['usuario'] = {
            'id':      self.user.id,
            'email':   self.user.email,
            'nombre':  self.user.nombre,
            'apellido': self.user.apellido,
            'rol':     self.user.rol.nombre if self.user.rol else None,
        }
        return data


class NegocioSerializer(serializers.ModelSerializer):
    propietario = UsuarioSerializer(read_only=True)

    class Meta:
        model  = Negocio
        fields = [
            'id', 'propietario', 'nombre', 'descripcion',
            'direccion', 'categoria', 'activo', 'created_at',
            'ruc', 'razon_social', 'telefono',
            'hora_apertura', 'hora_cierre', 'dias_atencion',
        ]


class NegocioCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Negocio
        fields = [
            'nombre', 'descripcion', 'direccion', 'categoria',
            'ruc', 'razon_social', 'telefono',
            'hora_apertura', 'hora_cierre', 'dias_atencion',
        ]

    def create(self, validated_data):
        return Negocio.objects.create(**validated_data)


class ProductoSerializer(serializers.ModelSerializer):
    categoria_label = serializers.SerializerMethodField()

    class Meta:
        model  = Producto
        fields = [
            'id', 'negocio', 'nombre', 'descripcion', 'precio', 'categoria', 'categoria_label', 'disponible', 'created_at', 'updated_at'
        ]
        read_only_fields = ['negocio', 'created_at', 'updated_at']

    def get_categoria_label(self, obj):
        return obj.get_categoria_display()
    
class HistorialCambioSerializer(serializers.ModelSerializer):
    tipo_cambio_label = serializers.SerializerMethodField()
    usuario_nombre    = serializers.SerializerMethodField()
    producto_nombre   = serializers.CharField(source='producto.nombre', read_only=True)

    class Meta:
        model  = HistorialCambioProducto
        fields = [
            'id', 'producto', 'producto_nombre',
            'usuario', 'usuario_nombre',
            'tipo_cambio', 'tipo_cambio_label',
            'valor_anterior', 'valor_nuevo', 'comentario', 'fecha'
        ]

    def get_tipo_cambio_label(self, obj):
        return obj.get_tipo_cambio_display()

    def get_usuario_nombre(self, obj):
        if obj.usuario:
            return f'{obj.usuario.nombre} {obj.usuario.apellido}'.strip()
        return 'Sistema'


class DetallePedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model  = DetallePedido
        fields = ['id', 'producto', 'cantidad', 'precio_unitario']


class HistorialEstadoPedidoSerializer(serializers.ModelSerializer):
    estado_anterior_label = serializers.SerializerMethodField()
    estado_nuevo_label    = serializers.SerializerMethodField()
    cambiado_por_nombre   = serializers.SerializerMethodField()

    class Meta:
        model  = HistorialEstadoPedido
        fields = [
            'id', 'pedido',
            'estado_anterior', 'estado_anterior_label',
            'estado_nuevo', 'estado_nuevo_label',
            'cambiado_por', 'cambiado_por_nombre',
            'comentario', 'fecha',
        ]

    def _label_estado(self, estado):
        mapa = dict(Pedido.ESTADOS)
        return mapa.get(estado, estado or '')

    def get_estado_anterior_label(self, obj):
        return self._label_estado(obj.estado_anterior)

    def get_estado_nuevo_label(self, obj):
        return self._label_estado(obj.estado_nuevo)

    def get_cambiado_por_nombre(self, obj):
        if obj.cambiado_por:
            return f'{obj.cambiado_por.nombre} {obj.cambiado_por.apellido}'.strip()
        return 'Sistema'


class NegocioMiniSerializer(serializers.ModelSerializer):
    """Versión reducida del negocio para anidar en PedidoSerializer."""
    class Meta:
        model  = Negocio
        fields = ['id', 'nombre', 'categoria', 'direccion', 'telefono']


class PedidoSerializer(serializers.ModelSerializer):
    detalles            = DetallePedidoSerializer(many=True, read_only=True)
    cliente             = UsuarioSerializer(read_only=True)
    repartidor          = UsuarioSerializer(read_only=True)
    negocio_info        = NegocioMiniSerializer(source='negocio', read_only=True)
    estado_label        = serializers.SerializerMethodField()
    historial_estados   = HistorialEstadoPedidoSerializer(many=True, read_only=True)

    class Meta:
        model  = Pedido
        fields = [
            'id', 'cliente', 'negocio', 'negocio_info', 'repartidor',
            'estado', 'estado_label', 'total',
            'direccion_entrega', 'lat_entrega', 'lng_entrega',
            'detalles', 'historial_estados',
            'created_at', 'updated_at',
        ]

    def get_estado_label(self, obj):
        return obj.get_estado_display()