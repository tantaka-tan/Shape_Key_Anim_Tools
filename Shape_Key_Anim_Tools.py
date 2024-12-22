import bpy

bl_info = {
    "name": "Shape_Key_Anim_Tools ",
    "description": "シェイプキーのアニメーション入力に関するアドオンです。すべてのキー、アクティブなキー、ミュートのキーを入力できます。また、現在のキーフレームを指定した先に複製もできます。",
    "author": "Tantaka",
    "version": (1, 12, 5),
    "blender": (3, 6, 0),
    "category": "Object",
}
# オペレーター: すべてのシェイプキーを入力

class OBJECT_OT_keyframe_all_shape_keys(bpy.types.Operator):
    bl_idname = "object.keyframe_all_shape_keys"
    bl_label = "すべてのシェイプキーを入力"
    bl_description = "すべてのシェイプキーの現在のまま入力"

    def execute(self, context):
        obj = context.active_object
        if obj and obj.data.shape_keys:
            for key_block in obj.data.shape_keys.key_blocks:
                key_block.keyframe_insert(data_path="value", frame=context.scene.frame_current)
            self.report({'INFO'}, "すべてのシェイプキーにキーフレームを挿入しました")
        else:
            self.report({'WARNING'}, "シェイプキーを持つオブジェクトが選択されていません")
        return {'FINISHED'}


# オペレーター: すべてのシェイプキーをリセット
class OBJECT_OT_reset_all_shape_keys(bpy.types.Operator):
    bl_idname = "object.reset_all_shape_keys"
    bl_label = "アクティブなシェイプキーのキーフレームを0で入力"
    bl_description = "選択したオブジェクトのすべてのシェイプキーを0にリセット"

    def execute(self, context):
        obj = context.active_object
        if obj and obj.data.shape_keys:
            for key_block in obj.data.shape_keys.key_blocks:
                key_block.value = 0.0
            self.report({'INFO'}, "すべてのシェイプキーを0にリセットしました")
        return {'FINISHED'}

# オペレーター: 全てのシェイプキーをリセットしてキーフレームを挿入
class OBJECT_OT_reset_key_all_shape_keys(bpy.types.Operator):
    bl_idname = "object.reset_key_all_shape_keys"
    bl_label = "すべてのシェイプキーのシェイプキーを0の値で入力"
    bl_description = "すべてのシェイプキーを0にリセットしてキーフレームを挿入"

    def execute(self, context):
        obj = context.active_object
        if obj and obj.data.shape_keys:
            for key_block in obj.data.shape_keys.key_blocks:
                key_block.value = 0.0
                key_block.keyframe_insert(data_path="value", frame=context.scene.frame_current)
            self.report({'INFO'}, "すべてのシェイプキーをリセットし、キーフレームを挿入しました")
        return {'FINISHED'}

# オペレーター: ミュートされていないシェイプキーにキーフレームを挿入
class OBJECT_OT_keyframe_non_muted_shape_keys(bpy.types.Operator):
    bl_idname = "object.keyframe_non_muted_shape_keys"
    bl_label = "ミュート以外のシェイプキーを現在のまま入力"
    bl_description = "ミュートされていないすべてのシェイプキーにキーフレームを挿入"

    def execute(self, context):
        obj = context.active_object
        if obj and obj.data.shape_keys:
            for key_block in obj.data.shape_keys.key_blocks:
                if not key_block.mute:
                    key_block.keyframe_insert(data_path="value", frame=context.scene.frame_current)
            self.report({'INFO'}, "ミュート以外のシェイプキーにキーフレームを挿入しました")
        return {'FINISHED'}

# オペレーター: ミュート以外のシェイプキーを0の値で挿入
class OBJECT_OT_keyframe_non_muted_shape_keys_zero(bpy.types.Operator):
    bl_idname = "object.keyframe_non_muted_shape_keys_zero"
    bl_label = "ミュート以外のシェイプキーを0の値で入力"
    bl_description = "ミュートされていないすべてのシェイプキーに値0のキーフレームを挿入"

    def execute(self, context):
        obj = context.active_object
        if obj and obj.data.shape_keys:
            for key_block in obj.data.shape_keys.key_blocks:
                if not key_block.mute:
                    key_block.value = 0.0
                    key_block.keyframe_insert(data_path="value", frame=context.scene.frame_current)
            self.report({'INFO'}, "ミュート以外のシェイプキーに値0のキーフレームを挿入しました")
        return {'FINISHED'}


# 改善されたオペレーター: キーフレームのコピーと貼り付け
class OBJECT_OT_copy_paste_keyframe_with_popup(bpy.types.Operator):
    bl_idname = "object.copy_paste_keyframe_with_popup"
    bl_label = "現在のフレームを指定したフレーム先に複製"
    bl_description = "現在のフレームを指定したフレーム先に複製し、貼り付けたフレームに移動します"
    bl_options = {'REGISTER', 'UNDO'}

    frame_offset: bpy.props.IntProperty(
        name="フレームオフセット",
        description="現在のフレームから何フレーム先にコピーするかを指定します",
        default=1,
        min=1,
    )

    def execute(self, context):
        obj = context.active_object

        # アクティブオブジェクトとシェイプキーの存在チェック
        if obj is None:
            self.report({'WARNING'}, "アクティブなオブジェクトが選択されていません")
            return {'CANCELLED'}

        if not obj.data.shape_keys:
            self.report({'WARNING'}, "選択したオブジェクトにはシェイプキーがありません")
            return {'CANCELLED'}

        current_frame = context.scene.frame_current
        next_frame = current_frame + self.frame_offset

        shape_keys = obj.data.shape_keys.key_blocks
        for key_block in shape_keys:
            # 現在のフレームにキーフレームが存在するか確認
            animation_data = key_block.id_data.animation_data
            if animation_data and animation_data.action:
                fcurves = animation_data.action.fcurves
                for fcurve in fcurves:
                    if fcurve.data_path == f'key_blocks["{key_block.name}"].value':
                        # 現在のフレームにキーフレームが存在するか確認
                        for keyframe_point in fcurve.keyframe_points:
                            if int(keyframe_point.co.x) == current_frame:
                                # 現在のフレームの値を取得し、次のフレームに複製
                                key_block.keyframe_insert(data_path="value", frame=next_frame)
                                break

        # 貼り付けたフレームに移動
        context.scene.frame_current = next_frame
        self.report({'INFO'}, f"フレーム{current_frame}のキーフレームをフレーム{next_frame}にコピーして移動しました")
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

# ドロップダウンメニュー
class VIEW3D_MT_shape_key_menu(bpy.types.Menu):
    bl_label = "キーフレームを挿入"
    bl_idname = "VIEW3D_MT_shape_key_menu"

    def draw(self, context):
        layout = self.layout
        layout.operator(OBJECT_OT_keyframe_all_shape_keys.bl_idname, text="すべてのシェイプキーを現在のまま入力") 
        layout.operator(OBJECT_OT_reset_key_all_shape_keys.bl_idname, text="すべてのシェイプキーを0の値で入力")
        layout.operator(OBJECT_OT_reset_all_shape_keys.bl_idname, text="アクティブなシェイプキーを0の値で入力")
        layout.operator(OBJECT_OT_keyframe_non_muted_shape_keys.bl_idname, text="ミュート以外のシェイプキーを現在のまま入力")
        layout.operator(OBJECT_OT_keyframe_non_muted_shape_keys_zero.bl_idname, text="ミュート以外のシェイプキーを0の値で入力")


        # 「現在のキーフレームを指定したフレーム先に複製」はここでは表示しない

# パネルに統合
class DATA_PT_shape_keys_tools(bpy.types.Panel):
    bl_label = "Shape Key Tools"
    bl_idname = "DATA_PT_shape_keys_tools"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    bl_parent_id = "DATA_PT_shape_keys"
    bl_order = -1

    def draw(self, context):
        layout = self.layout
        layout.label(text="シェイプキーのツール", icon='SHAPEKEY_DATA')
        layout.menu(VIEW3D_MT_shape_key_menu.bl_idname, text="キーフレームを挿入")
        layout.operator(OBJECT_OT_copy_paste_keyframe_with_popup.bl_idname, text="現在のキーを指定したフレーム先に複製")

# 登録と登録解除
classes = [
    OBJECT_OT_reset_all_shape_keys,
    OBJECT_OT_reset_key_all_shape_keys,
    OBJECT_OT_keyframe_all_shape_keys,
    OBJECT_OT_keyframe_non_muted_shape_keys,
    OBJECT_OT_keyframe_non_muted_shape_keys_zero,
    OBJECT_OT_copy_paste_keyframe_with_popup,
    VIEW3D_MT_shape_key_menu,
    DATA_PT_shape_keys_tools,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
