"""
Model exported as python.
Name : Retract lines
Group : 
With QGIS : 31616
"""

from qgis.core import QgsVectorLayer
from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterFeatureSource
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsProcessingParameterNumber
import processing

class RetractLines(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSource('Input', 'Input line', types=[QgsProcessing.TypeVectorLine], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Extended', 'Extended', type=QgsProcessing.TypeVectorLine, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterNumber('Start', 'Start distance', type=QgsProcessingParameterNumber.Double, minValue=-1.79769e+308, maxValue=0, defaultValue=0))
        self.addParameter(QgsProcessingParameterNumber('End', 'End distance', type=QgsProcessingParameterNumber.Double, minValue=-1.79769e+308, maxValue=0, defaultValue=0))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(1, model_feedback)
        results = {}
        outputs = {}
        # Hack to load FeatureSource into memory without hiccups
        alg_params = {
            'END_DISTANCE': 0,
            'INPUT': parameters['Input'],
            'START_DISTANCE': 0,
            'OUTPUT': 'TEMPORARY_OUTPUT'
        }
        input = processing.run('native:extendlines', alg_params, feedback=feedback)['OUTPUT']
        
        # Extend lines
        alg_params = {
            'END_DISTANCE': abs(parameters['End']),
            'INPUT': parameters['Input'],
            'START_DISTANCE': abs(parameters['Start']),
            'OUTPUT': parameters['Extended']
        }
        extended = processing.run('native:extendlines', alg_params, feedback=feedback)['OUTPUT']
        f = extended.getFeature(1)
        
        # only non multi part geom is supported
        feedback.pushInfo(f"""\n
        layer input:{input}\n---\n
        layer extended:{extended}\n
        geometry:{f.geometry()}\n
        first vertex:{f.geometry().asPolyline()[0].y()}\n
        last vertex:{f.geometry().asPolyline()[-1].y()}
        \n""")
        input_first_vertex_xy, input_last_vertex_xy = input.getFeature(1).geometry().asPolyline()[0], input.getFeature(1).geometry().asPolyline()[-1]
        extended_first_vertex_xy, extended_last_vertex_xy = extended.getFeature(1).geometry().asPolyline()[0], extended.getFeature(1).geometry().asPolyline()[-1]
        x_first_vertex_offset,y_first_vertex_offset = input_first_vertex_xy.x()-extended_first_vertex_xy.x(), input_first_vertex_xy.y()-extended_first_vertex_xy.y()
        x_last_vertex_offset,y_last_vertex_offset = input_last_vertex_xy.x()-extended_last_vertex_xy.x(), input_last_vertex_xy.y()-extended_last_vertex_xy.y()
        
        
        feedback.pushInfo(f"""\n
            (({input_first_vertex_xy.x()+(x_first_vertex_offset*-1)},{input_first_vertex_xy.y()+(y_first_vertex_offset*-1)}),
            ({input_last_vertex_xy.x()+(x_last_vertex_offset*-1)},{input_last_vertex_xy.y()+(y_last_vertex_offset*-1)}))
        \n""")
        # Check if length of first and last segments, or the single segment (if only 2 vertices), is greater than or equal to the end and start distance.
        # If equal, then create line without first and last vertices. If greater, raise exception
        # Create geom from vertices with recalculated first and last vertex for each feature in input and create vector layer with the new features
        # See https://docs.qgis.org/3.16/en/docs/pyqgis_developer_cookbook/vector.html#creating-vector-layers
        #outputs['Extended'] = processing.run('native:extendlines', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        #results['Extended'] = outputs['Extended']['OUTPUT']
        return results
    
    def name(self):
        return 'Retract lines'

    def displayName(self):
        return 'Retract lines'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return RetractLines()
