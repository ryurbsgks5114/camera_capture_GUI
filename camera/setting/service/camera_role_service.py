
def assign_camera_role(camera_config, camera_id, selected_role):
    """선택한 카메라의 역할을 변경하고 새로운 설정을 반환합니다.

    Side와 Top 역할이 동일한 카메라에 중복 지정되지 않도록 처리합니다.

    Args:
        camera_config (dict): 기존 카메라 역할 설정
        camera_id (str): 역할을 변경할 카메라 ID
        selected_role (str): 지정할 역할 (Side, Top, 미지정)

    Returns:
        dict: 변경된 카메라 역할 설정
    """
    side_camera_id = camera_config.get("side_camera_id")
    top_camera_id = camera_config.get("top_camera_id")

    if selected_role == "Side":
        side_camera_id = camera_id

        if top_camera_id == camera_id:
            top_camera_id = None
    elif selected_role == "Top":
        top_camera_id = camera_id

        if side_camera_id == camera_id:
            side_camera_id = None
    elif selected_role == "미지정":
        if side_camera_id == camera_id:
            side_camera_id = None

        if top_camera_id == camera_id:
            top_camera_id = None

    return {
        "side_camera_id": side_camera_id,
        "top_camera_id": top_camera_id,
    }
