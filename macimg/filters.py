from typing import Union

import AppKit
import Quartz

from .core import Color, Image

class Filter:
    def __init__(self, filter_name):
        self._size = None
        self._bounds = None
        self._cifilter = Quartz.CIFilter.filterWithName_(filter_name)
        self._cifilter.setDefaults()

    def apply_to(self, image: Image) -> Image:
        """Applies the filter to an image.

        :param image: The image to apply the filter to
        :type image: Image
        :return: The modified image
        :rtype: Image

        .. versionadded:: 0.0.1
        """
        if self._bounds is None:
            self._bounds = AppKit.NSMakeRect(0, 0, image.size[0], image.size[1])

        ciimage = Quartz.CIImage.imageWithData_(image.data)
        self._cifilter.setValue_forKey_(ciimage, "inputImage")

        uncropped =  self._cifilter.valueForKey_(Quartz.kCIOutputImageKey)

        # Crop the result to the original image size
        cropped = uncropped.imageByCroppingToRect_(self._bounds)

        # Convert back to NSImage
        rep = AppKit.NSCIImageRep.imageRepWithCIImage_(cropped)
        result = AppKit.NSImage.alloc().initWithSize_(rep.size())
        result.addRepresentation_(rep)

        image._nsimage = Image(result)._nsimage
        image.modified = True
        return image

class AutoEnhance(Filter):
    """Attempts to enhance the image by applying suggested filters.

    :param correct_red_eye: Whether to attempt red eye removal, defaults to False
    :type correct_red_eye: bool, optional
    :param crop_to_features: Whether to crop the image to focus on the main features with it, defaults to False
    :type crop_to_features: bool, optional
    :param correct_rotation: Whether attempt perspective correction by rotating the image, defaults to False
    :type correct_rotation: bool, optional

    .. versionadded:: 0.0.1
    """
    def __init__(self, correct_red_eye: bool = False, crop_to_features: bool = False, correct_rotation: bool = False):
        self.correct_red_eye = correct_red_eye
        self.crop_to_features = crop_to_features
        self.correct_rotation = correct_rotation

    def apply_to(self, image: Image) -> Image:
        ciimage = Quartz.CIImage.imageWithData_(image.data)
        options = {
            Quartz.kCIImageAutoAdjustRedEye: self.correct_red_eye,
            Quartz.kCIImageAutoAdjustCrop: self.crop_to_features,
            Quartz.kCIImageAutoAdjustLevel: self.correct_rotation
        }
        enhancements = ciimage.autoAdjustmentFiltersWithOptions_(options)

        for filter in enhancements:
            filter.setValue_forKey_(ciimage, "inputImage")
            ciimage = filter.outputImage()

        # Crop the result to the original image size
        cropped = ciimage.imageByCroppingToRect_(Quartz.CGRectMake(0, 0, image.size[0] * 2, image.size[1] * 2))

        # Convert back to NSImage
        rep = AppKit.NSCIImageRep.imageRepWithCIImage_(cropped)
        result = AppKit.NSImage.alloc().initWithSize_(rep.size())
        result.addRepresentation_(rep)
        return Image(result)

class Bloom(Filter):
    """Applies a bloom effect to the image. Softens edges and adds a glow.

    :param intensity: The strength of the softening and glow effects, defaults to 0.5
    :type intensity: float

    .. versionadded:: 0.0.1
    """
    def __init__(self, intensity: float = 0.5):
        super().__init__("CIBloom")
        self.intensity = intensity

    def apply_to(self, image: Image) -> Image:
        self._cifilter.setValue_forKey_(self.intensity, "inputIntensity")
        return super().apply_to(image)

class Comic(Filter):
    """Applies a comic filter to the image. Outlines edges and applies a color halftone effect.

    .. versionadded:: 0.0.1
    """
    def __init__(self):
        super().__init__("CIComicEffect")

class Crystallize(Filter):
    """Applies a crystallization filter to the image. Creates polygon-shaped color blocks by aggregating pixel values.

    :param crystal_size: The radius of the crystals, defaults to 20.0
    :type crystal_size: float

    .. versionadded:: 0.0.1
    """
    def __init__(self, crystal_size: float = 20.0):
        super().__init__("CICrystallize")
        self.crystal_size = crystal_size

    def apply_to(self, image: Image) -> Image:
        self._cifilter.setValue_forKey_(self.crystal_size, "inputRadius")
        return super().apply_to(image)

class DepthOfField(Filter):
    """Applies a depth of field filter to the image, simulating a tilt & shift effect.

    :param focal_region: Two points defining a line within the image to focus the effect around (pixels around the line will be in focus), or None to use the center third of the image, defaults to None
    :type focal_region: Union[tuple[tuple[int, int], tuple[int, int]], None]
    :param intensity: Controls the amount of distance around the focal region to keep in focus. Higher values decrease the distance before the out-of-focus effect starts. Defaults to 10.0
    :type intensity: float
    :param focal_region_saturation: Adjusts the saturation of the focial region. Higher values increase saturation. Defaults to 1.5 (1.5x default saturation)
    :type focal_region_saturation: float

    .. versionadded:: 0.0.1
    """
    def __init__(self, focal_region: Union[tuple[tuple[int, int], tuple[int, int]], None] = None, intensity: float = 100.0, focal_region_saturation: float = 1.5):
        super().__init__("CIDepthOfField")
        self.focal_region = focal_region
        self.intensity = intensity
        self.focal_region_saturation = focal_region_saturation

    def apply_to(self, image: Image) -> Image:        
        if self.focal_region is None:
            center_top = Quartz.CIVector.vectorWithX_Y_(image.size[0] / 3, image.size[1] / 2)
            center_bottom = Quartz.CIVector.vectorWithX_Y_(image.size[0] * 3 / 2, image.size[1] / 2)
            self.focal_region = (center_top, center_bottom)
        elif isinstance(self.focal_region, tuple):
            point1 = Quartz.CIVector.vectorWithX_Y_(self.focal_region[0])
            point2 = Quartz.CIVector.vectorWithX_Y_(self.focal_region[1])
            self.focal_region = (point1, point2)

        self._cifilter.setValue_forKey_(self.focal_region[0], "inputPoint0")
        self._cifilter.setValue_forKey_(self.focal_region[1], "inputPoint1")
        self._cifilter.setValue_forKey_(self.intensity, "inputRadius")
        self._cifilter.setValue_forKey_(self.focal_region_saturation, "inputSaturation")
        return super().apply_to(image)

class Edges(Filter):
    """Detects the edges in the image and highlights them colorfully, blackening other areas of the image.

    :param intensity: The degree to which edges are highlighted. Higher is brighter. Defaults to 1.0
    :type intensity: float

    .. versionadded:: 0.0.1
    """
    def __init__(self, intensity: float = 1.0):
        super().__init__("CIEdges")
        self.intensity = intensity

    def apply_to(self, image: Image) -> Image:
        self._cifilter.setValue_forKey_(self.intensity, "inputIntensity")
        return super().apply_to(image)

class GaussianBlur(Filter):
    """Blurs the image using a Gaussian filter.

    :param intensity: The strength of the blur effect, defaults to 10
    :type intensity: float

    .. versionadded:: 0.0.1
    """
    def __init__(self, intensity: float = 10):
        super().__init__("CIGaussianBlur")
        self.intensity = intensity

    def apply_to(self, image: Image) -> Image:
        self._cifilter.setValue_forKey_(self.intensity, "inputRadius")
        return super().apply_to(image)

class Invert(Filter):
    """Inverts the color of the image.

    .. versionadded:: 0.0.1
    """
    def __init__(self):
        super().__init__("CIColorInvert")

class Monochrome(Filter):
    """Remaps the colors of the image to shades of the specified color.

    :param color: The color of map the image's colors to
    :type color: Color
    :param intensity: The strength of recoloring effect. Higher values map colors to darker shades of the provided color. Defaults to 1.0
    :type intensity: float

    .. versionadded:: 0.0.1
    """
    def __init__(self, color: Color, intensity: float = 1.0):
        super().__init__("CIColorMonochrome")
        self.color = color
        self.intensity = intensity

    def apply_to(self, image: Image) -> Image:
        cicolor = Quartz.CIColor.alloc().initWithColor_(self.color._nscolor)
        self._cifilter.setValue_forKey_(cicolor, "inputColor")
        self._cifilter.setValue_forKey_(self.intensity, "inputIntensity")
        return super().apply_to(image)

class NoiseReduction(Filter):
    """Reduces noise in the image by sharpening areas with a luminance delta below the specified noise level threshold.

    :param noise_level: The threshold for luminance changes in an area below which will be considered noise, defaults to 0.02
    :type noise_level: float
    :param sharpness: The sharpness of the resulting image, defaults to 0.4
    :type sharpness: float

    .. versionadded:: 0.0.1
    """
    def __init__(self, noise_level: float = 0.02, sharpness: float = 0.4):
        super().__init__("CINoiseReduction")
        self.noise_level = noise_level
        self.sharpness = sharpness

    def apply_to(self, image: Image) -> Image:
        self._cifilter.setValue_forKey_(self.noise_level, "inputNoiseLevel")
        self._cifilter.setValue_forKey_(self.sharpness, "inputSharpness")
        return super().apply_to(image)

class Outline(Filter):
    """Outlines detected edges within the image in black, leaving the rest transparent.

    :param threshold: The threshold to use when separating edge and non-edge pixels. Larger values produce thinner edge lines. Defaults to 0.1
    :type threshold: float

    .. versionadded:: 0.0.1
    """
    def __init__(self, threshold: float = 0.1):
        super().__init__("CILineOverlay")
        self.threshold = threshold

    def apply_to(self, image: Image) -> Image:
        self._cifilter.setValue_forKey_(self.threshold, "inputThreshold")
        return super().apply_to(image)

class Pixellate(Filter):
    """Pixellates the image.

    :param pixel_size: The size of the pixels, defaults to 8.0
    :type pixel_size: float

    .. versionadded:: 0.0.1
    """
    def __init__(self, pixel_size: float = 8.0):
        super().__init__("CIPixellate")
        self.pixel_size = pixel_size

    def apply_to(self, image: Image) -> Image:
        self._cifilter.setValue_forKey_(self.pixel_size, "inputScale")
        return super().apply_to(image)

class Pointillize(Filter):
    """Applies a pointillization filter to the image.

    :param crystal_size: The radius of the points, defaults to 20.0
    :type crystal_size: float

    .. versionadded:: 0.0.1
    """
    def __init__(self, point_size: float = 20.0):
        super().__init__("CIPointillize")
        self.point_size = point_size

    def apply_to(self, image: Image) -> Image:
        self._cifilter.setValue_forKey_(self.point_size, "inputRadius")
        return super().apply_to(image)

class Sepia(Filter):
    """Applies a sepia filter to the image; maps all colors of the image to shades of brown.

    :param intensity: The opacity of the sepia effect. A value of 0 will have no impact on the image. Defaults to 1.0
    :type intensity: float

    .. versionadded:: 0.0.1
    """
    def __init__(self, intensity: float = 1.0):
        super().__init__("CISepiaTone")
        self.intensity = intensity

    def apply_to(self, image: Image) -> Image:
        self._cifilter.setValue_forKey_(self.intensity, "inputIntensity")
        return super().apply_to(image)

class Vignette(Filter):
    """Applies vignette shading to the corners of the image.

    :param intensity: The intensity of the vignette effect, defaults to 1.0
    :type intensity: float

    .. versionadded:: 0.0.1
    """
    def __init__(self, intensity: float = 1.0):
        super().__init__("CIVignette")
        self.intensity = intensity

    def apply_to(self, image: Image) -> Image:
        self._cifilter.setValue_forKey_(self.intensity, "inputIntensity")
        return super().apply_to(image)