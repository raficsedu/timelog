def check_ownership(user, project_id):
    return True if user.my_projects.filter(pk=project_id) else False


def check_member_permission(user, member):
    return True if member.project.user_id == user.id or member.user_id == user.id else False
