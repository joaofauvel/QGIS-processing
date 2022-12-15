"""
Model exported as python.
Name : Mapped multiple offsets
Group : 
With QGIS : 31616
"""

from qgis.core import QgsExpression
from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterFeatureSource
from qgis.core import QgsProcessingParameterExpression
from qgis.core import QgsProcessingParameterNumber
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsProcessingParameterBoolean
from qgis.core import QgsProcessingParameterDefinition
import processing


class MappedMultipleOffsets(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSource('Inputlines', 'Input line(s)', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterExpression('Mappingspacingn', 'Mapping (spacing,n)', parentLayerParameterName='', defaultValue='array(array())'))
        self.addParameter(QgsProcessingParameterFeatureSink('ArrayOffsetLines', 'Array of offset lines', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))
        
        param = QgsProcessingParameterBoolean('Keepfirst', 'Keep first', defaultValue=True)
        param.setFlags(param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(param)
        
        param = QgsProcessingParameterBoolean('Firstoffsethalfspacing', 'First offset half spacing', defaultValue=False)
        param.setFlags(param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(param)

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(2, model_feedback)
        results = {}
        outputs = {}
        
        mapping = QgsExpression(parameters['Mappingspacingn']).evaluate()
        #dist_cum = 0
        feats = []
        input_line = parameters['Inputlines']
        for tup in mapping:
            s, n = tup
            for i in range(n):
                is_first = (i==0)
                is_last = (i==(n-1))
                # Offset lines
                alg_params = {
                    'DISTANCE': s/2 if (parameters['Firstoffsethalfspacing'] and is_first) else s,
                    'INPUT': input_line,
                    'JOIN_STYLE': 0,
                    'MITER_LIMIT': 2,
                    'SEGMENTS': 8,
                    'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
                }
                feat = processing.run('native:offsetline', alg_params, context=context, feedback=feedback, is_child_algorithm=True)['OUTPUT']
                feats.append(feat)
                input_line = feat
                if parameters['Firstoffsethalfspacing'] and is_last:
                    # Offset lines
                    alg_params = {
                        'DISTANCE': s/2,
                        'INPUT': input_line,
                        'JOIN_STYLE': 0,
                        'MITER_LIMIT': 2,
                        'SEGMENTS': 8,
                        'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
                    }
                    feat = processing.run('native:offsetline', alg_params, context=context, feedback=feedback, is_child_algorithm=True)['OUTPUT']
                    input_line = feat

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}
        
        if parameters['Keepfirst']:
            # Save vector features to file
            alg_params = {
                'DATASOURCE_OPTIONS': '',
                'INPUT': parameters['Inputlines'],
                'LAYER_NAME': '',
                'LAYER_OPTIONS': '',
                'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
            }
            feats.append(processing.run('native:savefeatures', alg_params, context=context, feedback=feedback, is_child_algorithm=True)['OUTPUT'])
        
        # Merge vector layers
        alg_params = {
            'CRS': 'ProjectCrs',
            'LAYERS': feats,
            'OUTPUT': parameters['ArrayOffsetLines']
        }
        outputs['MergeVectorLayers'] = processing.run('native:mergevectorlayers', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['ArrayOffsetLines'] = outputs['MergeVectorLayers']['OUTPUT']
        return results

    def name(self):
        return 'Mapped multiple offsets'

    def displayName(self):
        return 'Mapped multiple offsets'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return MappedMultipleOffsets()
