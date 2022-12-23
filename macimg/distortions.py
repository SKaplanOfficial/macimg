from typing import Union

import Quartz

from .core import Image
from .filters import Filter

class Bump(Filter):
    """Creates a concave (inward) or convex (outward) bump at the specified location within the image.

    :param center: The center point of the effect, or None to use the center of the image, defaults to None
    :type center: Union[tuple[int, int], None]
    :param radius: The radius of the bump in pixels, defaults to 300.0
    :type radius: float
    :param curvature: Controls the direction and intensity of the bump's curvature. Positive values create convex bumps while negative values create concave bumps. Defaults to 0.5
    :type curvature: float

    .. versionadded:: 0.0.1
    """
    def __init__(self, center: Union[tuple[int, int], None] = None, radius: float = 300.0, curvature: float = 0.5):
        super().__init__("CIBumpDistortion")
        self.center = center
        self.radius = radius
        self.curvature = curvature

    def apply_to(self, image: Image) -> Image:
        if self.center is None:
            self.center = Quartz.CIVector.vectorWithX_Y_(image.size[0] / 2, image.size[1] / 2)
        else:
            self.center = Quartz.CIVector.vectorWithX_Y_(self.center[0], self.center[1])

        self._cifilter.setValue_forKey_(self.center, "inputCenter")
        self._cifilter.setValue_forKey_(self.radius, "inputRadius")
        self._cifilter.setValue_forKey_(self.curvature, "inputScale")
        return super().apply_to(image)

class Pinch(Filter):
    """Creates an inward pinch distortion at the specified location within the image.

    :param center: The center point of the effect, or None to use the center of the image, defaults to None
    :type center: Union[tuple[int, int], None]
    :param intensity: Controls the scale of the pinch effect. Higher values stretch pixels away from the specified center to a greater degree. Defaults to 0.5
    :type intensity: float

    .. versionadded:: 0.0.1
    """
    def __init__(self, center: Union[tuple[int, int], None] = None, intensity: float = 0.5):
        super().__init__("CIPinchDistortion")
        self.center = center
        self.intensity = intensity

    def apply_to(self, image: Image) -> Image:
        if self.center is None:
            self.center = Quartz.CIVector.vectorWithX_Y_(image.size[0] / 2, image.size[1] / 2)
        else:
            self.center = Quartz.CIVector.vectorWithX_Y_(self.center[0], self.center[1])

        self._cifilter.setValue_forKey_(self.center, "inputCenter")
        self._cifilter.setValue_forKey_(self.intensity, "inputScale")
        return super().apply_to(image)

class Twirl(Filter):
    """Creates a reusable twirl distortion that rotates pixels around the specified location within an image.

    :param center: The center point of the effect, or None to use the center of the image, defaults to None
    :type center: Union[tuple[int, int], None]
    :param radius: The pixel radius around the centerpoint that defines the area to apply the effect to, defaults to 300.0
    :type radius: float
    :param angle: The angle of the twirl in radians, defaults to 3.14
    :type angle: float

    .. versionadded:: 0.0.1
    """
    def __init__(self, center: Union[tuple[int, int], None] = None, radius: float = 300.0, angle: float = 3.14):
        super().__init__("CITwirlDistortion")
        self.center = center
        self.radius = radius
        self.angle = angle

    def apply_to(self, image: Image) -> Image:
        if self.center is None:
            self.center = Quartz.CIVector.vectorWithX_Y_(image.size[0] / 2, image.size[1] / 2)
        else:
            self.center = Quartz.CIVector.vectorWithX_Y_(self.center[0], self.center[1])

        self._cifilter.setValue_forKey_(self.center, "inputCenter")
        self._cifilter.setValue_forKey_(self.radius, "inputRadius")
        self._cifilter.setValue_forKey_(self.angle, "inputAngle")
        return super().apply_to(image)
