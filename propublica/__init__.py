from .congress import members


def get_congress():
    """Temporary function for testing project structure"""
    return members.CongressMembers().get_all_members()
