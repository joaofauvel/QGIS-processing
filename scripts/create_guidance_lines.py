"""
Model exported as python.
Name : Create guidance lines
Group : 
With QGIS : 31616
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterNumber
from qgis.core import QgsProcessingParameterFeatureSource
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsProcessingParameterExpression
import processing


class CreateGuidanceLines(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSource('Masterlayer', 'Master layer', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterNumber('Treatments', 'Treatments', type=QgsProcessingParameterNumber.Integer, minValue=1, defaultValue=None))
        self.addParameter(QgsProcessingParameterExpression('Treatmentsspacingsfidsn', 'Treatments spacings (t,s,n)', parentLayerParameterName='Masterlayer', defaultValue='array(\r\n\tarray()\r\n)'))
        self.addParameter(QgsProcessingParameterNumber('Replications', 'Replications', type=QgsProcessingParameterNumber.Integer, minValue=1, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('NotFinal', 'not final', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue=None))


    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        outputs = {}
        
        
        # Mapped multiple offsets
        alg_params = {
            'Firstoffsethalfspacing': True,
            'Inputlines': parameters['Masterlayer'],
            'Keepfirst': True,
            'Mappingspacingn': parameters['Treatmentsspacingsfidsn'],
            'ArrayOffsetLines': parameters['NotFinal']
        }
        outputs['MappedMultipleOffsets'] = processing.run('script:Mapped multiple offsets', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['NotFinal'] = outputs['MappedMultipleOffsets']['ArrayOffsetLines']
        return results

    def name(self):
        return 'Create guidance lines'

    def displayName(self):
        return 'Create guidance lines'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return CreateGuidanceLines()
