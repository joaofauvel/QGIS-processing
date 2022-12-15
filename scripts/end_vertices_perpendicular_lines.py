"""
Model exported as python.
Name : Perpendicular lines along line
Group : 
With QGIS : 31616
"""

from qgis.core import QgsVectorLayer
from qgis.core import QgsExpression
from qgis.core import QgsExpressionContext
from qgis.core import QgsExpressionContextScope
from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterFeatureSource
from qgis.core import QgsProcessingParameterCrs
from qgis.core import QgsProcessingParameterNumber
from qgis.core import QgsProcessingParameterExpression
from qgis.core import QgsProcessingParameterBoolean
from qgis.core import QgsProcessingParameterFeatureSink
import processing


class PerpendicularLinesAlongLine(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSource('Inputlayer', 'Input layer', types=[QgsProcessing.TypeVectorLine,QgsProcessing.TypeVectorPolygon], defaultValue=None))
        # The CRS that the input layer should be converted to. If no conversion, then input the same as the layer's.
        self.addParameter(QgsProcessingParameterCrs('ConvertinputCRS', 'Convert input CRS to UTM', defaultValue='EPSG:4326'))
        self.addParameter(QgsProcessingParameterExpression('Distance', 'Distance', parentLayerParameterName='Inputlayer', defaultValue='0'))
        self.addParameter(QgsProcessingParameterNumber('Startoffset', 'Start offset', type=QgsProcessingParameterNumber.Double, minValue=0, defaultValue=0))
        self.addParameter(QgsProcessingParameterNumber('Endoffset', 'End offset', type=QgsProcessingParameterNumber.Double, minValue=0, defaultValue=0))
        self.addParameter(QgsProcessingParameterExpression('Geometryexpression', 'Geometry expression', parentLayerParameterName='', defaultValue='extend(\r\n   make_line(\r\n      $geometry,\r\n       project (\r\n          $geometry, \r\n          20, \r\n          radians(\"angle\"-90))\r\n        ),\r\n   20,\r\n   0\r\n)'))
        self.addParameter(QgsProcessingParameterCrs('OutputCRS', 'Output CRS', defaultValue='EPSG:4326'))
        self.addParameter(QgsProcessingParameterBoolean('VERBOSE_LOG', 'Verbose logging', optional=True, defaultValue=False))
        self.addParameter(QgsProcessingParameterFeatureSink('PerpendicularLines', 'Perpendicular lines', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, supportsAppend=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(4, model_feedback)
        results = {}
        outputs = {}

        # Reproject layer
        alg_params = {
            'INPUT': parameters['Inputlayer'],
            'OPERATION': '',
            'TARGET_CRS': parameters['ConvertinputCRS'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        layer = processing.run('native:reprojectlayer', alg_params)['OUTPUT']
        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}
        e = QgsExpression(parameters['Distance'])
        econtext = QgsExpressionContext()
        scope = QgsExpressionContextScope()
        econtext.appendScope(scope)
        e.prepare(econtext)
        scope.setFeature(next(layer.getFeatures()))
        # Points along geometry
        alg_params = {
            'DISTANCE': e.evaluate(econtext),
            'END_OFFSET': parameters['Endoffset'],
            'INPUT': layer,
            'START_OFFSET': parameters['Startoffset'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['PointsAlongLines'] = processing.run('native:pointsalonglines', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Geometry by expression
        alg_params = {
            'EXPRESSION': parameters['Geometryexpression'],
            'INPUT': outputs['PointsAlongLines']['OUTPUT'],
            'OUTPUT_GEOMETRY': 1,
            'WITH_M': False,
            'WITH_Z': False,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['GeometryByExpression'] = processing.run('native:geometrybyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Reproject layer
        alg_params = {
            'INPUT': outputs['GeometryByExpression']['OUTPUT'],
            'OPERATION': '',
            'TARGET_CRS': parameters['OutputCRS'],
            'OUTPUT': parameters['PerpendicularLines']
        }
        outputs['ReprojectLayer'] = processing.run('native:reprojectlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['PerpendicularLines'] = outputs['ReprojectLayer']['OUTPUT']
        return results

    def name(self):
        return 'Perpendicular lines along line'

    def displayName(self):
        return 'Perpendicular lines along line'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return PerpendicularLinesAlongLine()
