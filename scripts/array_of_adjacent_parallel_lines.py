"""
Model exported as python.
Name : Array of adjacent parallel lines
Group : 
With QGIS : 32208
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterFeatureSource
from qgis.core import QgsProcessingParameterDistance
from qgis.core import QgsProcessingParameterBoolean
from qgis.core import QgsProcessingParameterNumber
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class ArrayOfAdjacentParallelLines(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSource('inputlayer', 'Input layer', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterNumber('spacing', 'Spacing', type=QgsProcessingParameterNumber.Double, minValue=0, defaultValue=None))
        self.addParameter(QgsProcessingParameterNumber('numberofrightlines', 'Number of lines to the right', type=QgsProcessingParameterNumber.Integer, minValue=1, defaultValue=None))
        self.addParameter(QgsProcessingParameterNumber('numberofleftlines', 'Number of lines to the left', type=QgsProcessingParameterNumber.Integer, minValue=1, defaultValue=None))
        self.addParameter(QgsProcessingParameterBoolean('centeredlines', 'Middle is centered (adds one line in the middle)', defaultValue=False))
        self.addParameter(QgsProcessingParameterFeatureSink('OffsetLines', 'Offset lines', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(3, model_feedback)
        results = {}
        outputs = {}
        
        alg_output = []
        
        if parameters['centeredlines']:
            exp1 = f"array(array({parameters['spacing']},{parameters['numberofrightlines']}))"
            exp2 = f"array(array({parameters['spacing']*-1},{parameters['numberofleftlines']}))"
        else:
            exp1 = f"array(array({parameters['spacing']/2},1),array({parameters['spacing']},{parameters['numberofrightlines']-1}))"
            exp2 = f"array(array({(parameters['spacing']/2)*-1},1),array({parameters['spacing']*-1},{parameters['numberofleftlines']-1}))"
        
        # Mapped multiple offsets
        alg_params = {
            'Firstoffsethalfspacing': False,
            'Inputlines': parameters['inputlayer'],
            'Keepfirst': parameters['centeredlines'],
            'Mappingspacingn': exp1,
            'ArrayOffsetLines': QgsProcessing.TEMPORARY_OUTPUT
        }
        alg_output.append(processing.run('script:Mapped multiple offsets', alg_params, context=context, feedback=feedback, is_child_algorithm=True)['ArrayOffsetLines'])

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Mapped multiple offsets
        alg_params = {
            'Firstoffsethalfspacing': False,
            'Inputlines': parameters['inputlayer'],
            'Keepfirst': False,
            'Mappingspacingn': exp2,
            'ArrayOffsetLines': QgsProcessing.TEMPORARY_OUTPUT
        }
        alg_output.append(processing.run('script:Mapped multiple offsets', alg_params, context=context, feedback=feedback, is_child_algorithm=True)['ArrayOffsetLines'])

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Merge vector layers
        alg_params = {
            'CRS': None,
            'LAYERS': alg_output,
            'OUTPUT': parameters['OffsetLines']
        }
        outputs['MergeVectorLayers'] = processing.run('native:mergevectorlayers', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['OffsetLines'] = outputs['MergeVectorLayers']['OUTPUT']
        return results

    def name(self):
        return 'Array of adjacent parallel lines'

    def displayName(self):
        return 'Array of adjacent parallel lines'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return ArrayOfAdjacentParallelLines()
