from django.contrib import admin
from .models import (
    Usuario, Rol, Negocio, Producto, Pedido, DetallePedido,
    PasswordResetToken, HistorialCambioProducto, HistorialEstadoPedido,
)


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display  = ('email', 'nombre', 'apellido', 'rol', 'activo', 'created_at')
    list_filter   = ('activo', 'rol')
    search_fields = ('email', 'nombre', 'apellido')


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display  = ('nombre', 'negocio', 'precio', 'categoria', 'disponible', 'updated_at')
    list_filter   = ('disponible', 'categoria', 'negocio')
    search_fields = ('nombre', 'descripcion', 'negocio__nombre')


@admin.register(HistorialCambioProducto)
class HistorialCambioProductoAdmin(admin.ModelAdmin):
    list_display  = ('fecha', 'producto', 'tipo_cambio', 'valor_anterior', 'valor_nuevo', 'usuario')
    list_filter   = ('tipo_cambio', 'fecha')
    search_fields = ('producto__nombre', 'usuario__email')
    readonly_fields = ('fecha',)


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display  = ('id', 'cliente', 'negocio', 'repartidor', 'estado', 'total', 'created_at')
    list_filter   = ('estado', 'negocio')
    search_fields = ('cliente__email', 'cliente__nombre', 'negocio__nombre')


@admin.register(HistorialEstadoPedido)
class HistorialEstadoPedidoAdmin(admin.ModelAdmin):
    list_display  = ('fecha', 'pedido', 'estado_anterior', 'estado_nuevo', 'cambiado_por')
    list_filter   = ('estado_nuevo', 'fecha')
    search_fields = ('pedido__id', 'cambiado_por__email')
    readonly_fields = ('fecha',)


admin.site.register(Rol)
admin.site.register(Negocio)
admin.site.register(DetallePedido)
admin.site.register(PasswordResetToken)