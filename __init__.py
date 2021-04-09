bl_info = {
    "name": "Custom Preferences Size",
    "author": "Rombout Versluijs, Pan Beeb (Beep)",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "File > Edit > Custom Preferences Size",
    "description": "Set a custom size to the Preferences window",
    "wiki_url": "https://github.com/schroef/Custom-Window-Size",
    "tracker_url": "https://github.com/schroef/Custom-Window-Size/issues",
    "category": "Preferences",
}

import bpy
import rna_keymap_ui
from bpy.props import (
    StringProperty, IntProperty,
)
from bpy.types import (
    AddonPreferences, Operator
)


def get_hotkey_entry_item(km, kmi_name):
    for i, km_item in enumerate(km.keymap_items):
        if km.keymap_items.keys()[i] == kmi_name:
            return km_item
            
    return None

def call_preferences(self, context):
    preferences = context.preferences
    addon_prefs = preferences.addons[__name__].preferences

    # Modify scene settings
    render = bpy.context.scene.render
    prefs = bpy.context.preferences
    view = prefs.view
    orgResX = render.resolution_x
    orgResY = render.resolution_y
    render.resolution_x = int(addon_prefs.pref_window_width)
    render.resolution_y = int(addon_prefs.pref_window_height)
    orgDispMode = view.render_display_type
    view.render_display_type = "WINDOW"

    # Call image editor window
    bpy.ops.render.view_show("INVOKE_DEFAULT")

    # Change area type
    area = bpy.context.window_manager.windows[-1].screen.areas[0]
    area.type = "PREFERENCES"

    # Restore old values
    view.render_display_type = orgDispMode
    render.resolution_x = orgResX
    render.resolution_y = orgResY


class CPS_OT_CallPreferences(Operator):
    """Create a new Mesh Object"""
    bl_idname = "cps.call_preferences"
    bl_label = "Prefences"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        call_preferences(self, context)
        return {'FINISHED'}


class CPS_AddonPreferences(AddonPreferences):
    """ Preference Settings Addon Panel"""
    bl_idname = __name__

    pref_window_width: StringProperty(
        name="Window Width",
        description="Set width of the preferences window",
        default="1080",
        )

    pref_window_height: StringProperty(
        name="Window Height",
        description="Set width and height of the preferences window",
        default="720",
    )
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout = layout.column(align=True)
        layout.label(text = "Preferences Window Size")
        row = layout.row()
        row.label(text = "Width:")
        row.prop(self, "pref_window_width", text="")
        row.label(text = "Height:")
        row.prop(self, "pref_window_height", text="")
        
        layout.separator()
        layout = layout.box()
        wm = bpy.context.window_manager
        kc = wm.keyconfigs.user

        km = kc.keymaps['Screen']
        kmi = get_hotkey_entry_item(km, 'cps.call_preferences')
        if kmi:
            col = layout.row()
            col.label(text = "Opens Preferences with custom width")
            col = layout.row()
            col.context_pointer_set("keymap", km)
            rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
            col = layout.row()
            col.label(text = "Save keymap to keep changes", icon = 'ERROR')

        else:
            col = layout.row()
            col.label(text = "Personal setting")
            col.label(text = "restore hotkeys from interface tab")


# Registration
def cps_call_window(self, context):
    self.layout.operator(
        CPS_OT_CallPreferences.bl_idname,
        text="Custom Preferences",
        icon='PREFERENCES')

# This allows you to right click on a button and link to the manual
# def add_object_manual_map():
#     url_manual_prefix = "https://docs.blender.org/manual/en/dev/"
#     url_manual_mapping = (
#         ("bpy.ops.mesh.add_object", "editors/3dview/object"),
#         )
#     return url_manual_prefix, url_manual_mapping

addon_keymaps = []
classes = [
    CPS_AddonPreferences,
    CPS_OT_CallPreferences
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    # bpy.utils.register_manual_map(add_object_manual_map)
    bpy.types.TOPBAR_MT_edit.append(cps_call_window)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    km = kc.keymaps.new(name = "Screen", space_type = "EMPTY")
    kmi = km.keymap_items.new("cps.call_preferences", "COMMA", "PRESS", ctrl = True, shift = True)
    # kmi.properties.tab = "EXECUTE"
    addon_keymaps.append((km, kmi))


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    # bpy.utils.unregister_manual_map(add_object_manual_map)
    bpy.types.TOPBAR_MT_edit.remove(cps_call_window)

    # Clean the keymap
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()


if __name__ == "__main__":
    register()
