class ImageResponses:

    def __init__(self, id, image: dict, manual_tags: list, checked_tags: list, email: str = None) -> None:
        self.id = id
        self.image = image
        self.person = email
        self.manual_tags = manual_tags
        self.checked_tags = checked_tags

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'email': self.person,
            'image': self.image,
            'manual_tags': self.manual_tags,
            'checked_tags': self.checked_tags
        }
