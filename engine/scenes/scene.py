from engine.objects.model import SkyBox


class Scene:
    def __init__(self, app):
        self.app = app
        self.skybox = SkyBox(app)

    def render(self):
        self.skybox.render()
