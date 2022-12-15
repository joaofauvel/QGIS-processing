"""
Model exported as python.
Name : IDW Wrapper for Points
Group : 
With QGIS : 31616
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterBoolean
from qgis.core import QgsProcessingParameterCrs
from qgis.core import QgsProcessingParameterFeatureSource
from qgis.core import QgsProcessingParameterNumber
from qgis.core import QgsProcessingParameterExtent
from qgis.core import QgsProcessingParameterField
from qgis.core import QgsProcessingParameterFieldMapping
from qgis.core import QgsProcessingParameterRasterDestination
from qgis.core import QgsProcessingParameterString
from qgis.core import QgsProcessingParameterDefinition
import processing


class IdwWrapperPoints(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSource('Inputlayer', 'Input layer', types=[QgsProcessing.TypeVectorAnyGeometry], defaultValue=None))
        self.addParameter(QgsProcessingParameterNumber('InterpolationattributeID', 'Interpolation attribute index', type=QgsProcessingParameterNumber.Integer))
        self.addParameter(QgsProcessingParameterNumber('DistancecoefficientP', 'Distance coefficient P', type=QgsProcessingParameterNumber.Double, minValue=0, maxValue=99.99, defaultValue=2))
        self.addParameter(QgsProcessingParameterExtent('Extent', 'Extent', defaultValue=None))
        self.addParameter(QgsProcessingParameterNumber('Pixelsize', 'Pixel size', type=QgsProcessingParameterNumber.Double, defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterDestination('Clipped', 'Clipped', createByDefault=False, defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterDestination('Interpolated', 'Interpolated', createByDefault=True, defaultValue=None))
        
        param = QgsProcessingParameterBoolean('Clipbymask', 'Clip by mask', optional=True, defaultValue=False)
        param.setFlags(param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(param)
        param = QgsProcessingParameterFeatureSource('Masklayer', 'Mask layer', optional=True, types=[QgsProcessing.TypeVectorPolygon], defaultValue=None)
        param.setFlags(param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(param)
        param = QgsProcessingParameterCrs('SourceCRS', 'Source CRS', optional=True, defaultValue='EPSG:4326')
        param.setFlags(param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(param)
        param = QgsProcessingParameterCrs('TargetCRS', 'Target CRS', optional=True, defaultValue='EPSG:4326')
        param.setFlags(param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(param)
        param = QgsProcessingParameterNumber('nodatavalue', 'nodata value', optional=True, type=QgsProcessingParameterNumber.Double, defaultValue=None)
        param.setFlags(param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(param)
        param = QgsProcessingParameterString('Additionalcreationoptions', 'Additional creation options', optional=True, multiLine=False, defaultValue='COMPRESS=DEFLATE|PREDICTOR=2|ZLEVEL=9')
        param.setFlags(param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(param)

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        outputs = {}
        partial_outputs = {}

        # IDW interpolation
        alg_params = {
            'DISTANCE_COEFFICIENT': parameters['DistancecoefficientP'],
            'EXTENT': parameters['Extent'],
            'INTERPOLATION_DATA': f'{parameters["Inputlayer"]}::~::0::~::{parameters["InterpolationattributeID"]}::~::0',
            'PIXEL_SIZE': parameters['Pixelsize'],
            'OUTPUT': parameters['Interpolated'],
        }
        if parameters['Clipbymask']:
            partial_outputs['IdwInterpolation'] = processing.run('qgis:idwinterpolation', alg_params, context=None, feedback=feedback, is_child_algorithm=True)
            # Clip raster by mask layer
            alg_params = {
                'ALPHA_BAND': False,
                'CROP_TO_CUTLINE': True,
                'DATA_TYPE': 0,
                'EXTRA': '',
                'INPUT': partial_outputs['IdwInterpolation']['OUTPUT'],
                'KEEP_RESOLUTION': False,
                'MASK': parameters['Masklayer'],
                'MULTITHREADING': False,
                'NODATA': parameters['nodatavalue'],
                'OPTIONS': parameters['Additionalcreationoptions'],
                'SET_RESOLUTION': False,
                'SOURCE_CRS': parameters['SourceCRS'],
                'TARGET_CRS': parameters['TargetCRS'],
                'X_RESOLUTION': None,
                'Y_RESOLUTION': None,
                'OUTPUT': parameters['Clipped'],
            }
            partial_outputs['ClipRasterByMaskLayer'] = processing.run('gdal:cliprasterbymasklayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
            results['Interpolated'] = partial_outputs['ClipRasterByMaskLayer']['OUTPUT']
        else:
            partial_outputs['IdwInterpolation'] = processing.run('qgis:idwinterpolation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
            results['Interpolated'] = partial_outputs['IdwInterpolation']['OUTPUT']
        return results

    def name(self):
        return 'IdwWrapperPoints'

    def displayName(self):
        return 'IDW Wrapper for Points'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return IdwWrapperPoints()
