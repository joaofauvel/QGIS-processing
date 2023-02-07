"""
Model exported as python.
Name : Join multiple layers attributes by location
Group : 
With QGIS : 32802
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterMultipleLayers
from qgis.core import QgsProcessingParameterString
from qgis.core import QgsProcessingParameterNumber
from qgis.core import QgsProcessingParameterBoolean
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class JoinMultipleLayersAttributesByLocation(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterMultipleLayers('layers', 'Layers', layerType=QgsProcessing.TypeMapLayer, defaultValue=None))
        self.addParameter(QgsProcessingParameterString('geometry_predicate', 'Geometry predicate (comma separated indices). Example: 0,1,2', multiLine=False, defaultValue='0'))
        self.addParameter(QgsProcessingParameterString('fields', 'Fields to add (leave empty for all fields). Example: NDVI,VALUE', optional=True, multiLine=False, defaultValue=''))
        self.addParameter(QgsProcessingParameterNumber('join_type', 'Join type', type=QgsProcessingParameterNumber.Integer, minValue=0, maxValue=3, defaultValue=0))
        self.addParameter(QgsProcessingParameterBoolean('discard', 'Discard records which could not be joined', defaultValue=False))
        self.addParameter(QgsProcessingParameterString('joined_prefix', 'Joined prefix', optional=True, multiLine=False, defaultValue=''))
        self.addParameter(QgsProcessingParameterFeatureSink('Joined', 'Joined', optional=True, type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        outputs = {}
        
        first_layer = parameters['layers'][0]
        other_layers = parameters['layers'][1:]
        for index, l in enumerate(other_layers):
            # Join attributes by location
            alg_params = {
                'DISCARD_NONMATCHING': parameters['discard'],
                'INPUT': first_layer if index == 0 else partial,
                'JOIN': l,
                'JOIN_FIELDS': parameters['fields'].split(','),
                'METHOD': parameters['join_type'],
                'PREDICATE': parameters['geometry_predicate'].split(','),
                'PREFIX': parameters['joined_prefix'],
                'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
            }
            partial = processing.run('native:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)['OUTPUT']
        # Save vector features to file
        alg_params = {
            'DATASOURCE_OPTIONS': '',
            'INPUT': partial,
            'LAYER_NAME': '',
            'LAYER_OPTIONS': '',
            'OUTPUT': parameters['Joined']
        }
        output = processing.run('native:savefeatures', alg_params, context=context, feedback=feedback, is_child_algorithm=True)['OUTPUT']
        results['Joined'] = output
        return results

    def name(self):
        return 'Join multiple layers attributes by location'

    def displayName(self):
        return 'Join multiple layers attributes by location'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return JoinMultipleLayersAttributesByLocation()
