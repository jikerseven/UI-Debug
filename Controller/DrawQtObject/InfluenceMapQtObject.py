# Under MIT License, see LICENSE.txt

from PyQt4.QtGui import QPixmap
from PyQt4.QtGui import QPainter

from Controller.DrawQtObject.BaseDrawObject import BaseDrawObject
from Controller.QtToolBox import QtToolBox
from Model.DataIn.DrawingDataIn.DrawInfluenceMapDataIn import DrawInfluenceMapDataIn

__author__ = 'RoboCupULaval'


class InfluenceMapQtObject(BaseDrawObject):
    def __init__(self, data_in):
        BaseDrawObject.__init__(self, data_in)
        self._pixmap = None

    def _draw_pixmap(self):
        # Calcul de la taille des rectangles
        width = QtToolBox.field_ctrl.size[0] * QtToolBox.field_ctrl.ratio_screen
        height = QtToolBox.field_ctrl.size[1] * QtToolBox.field_ctrl.ratio_screen
        self._pixmap = QPixmap(width, height)
        painter = QPainter(self._pixmap)
        nb_width, nb_height = self.data['size']
        ref_x, ref_y = 0, 0
        rect_width = QtToolBox.field_ctrl.size[0] * QtToolBox.field_ctrl.ratio_screen / nb_width
        rect_height = QtToolBox.field_ctrl.size[1] * QtToolBox.field_ctrl.ratio_screen / nb_height

        # Paramétrage du pinceau
        painter.setPen(QtToolBox.create_pen(color=self.data['grid_color'],
                                            style=self.data['grid_style'],
                                            width=self.data['grid_width'],
                                            is_hide=not self.data['has_grid']))

        for nb_line, line in enumerate(self.data['field_data']):
            for nb_col, case in enumerate(line):
                if case > self.data['hottest_numb']:
                    case = self.data['hottest_numb']
                if case < self.data['coldest_numb']:
                    case = self.data['coldest_numb']
                rgb_value = InfluenceMapQtObject._convert_rgb_value_with_minmax(case,
                                                                                self.data['coldest_numb'],
                                                                                self.data['hottest_numb'],
                                                                                self.data['coldest_color'],
                                                                                self.data['hottest_color'])
                # Création de la brosse
                painter.setBrush(QtToolBox.create_brush(rgb_value))
                painter.drawRect(ref_x + rect_width * nb_col,
                                 ref_y + rect_height * nb_line,
                                 rect_width,
                                 rect_height)

    def draw(self, painter):
        if self._pixmap is None:
            self._draw_pixmap()

        if self.isVisible():
            x = QtToolBox.field_ctrl.marge * QtToolBox.field_ctrl.ratio_screen
            y = QtToolBox.field_ctrl.marge * QtToolBox.field_ctrl.ratio_screen
            width = QtToolBox.field_ctrl.size[0] * QtToolBox.field_ctrl.ratio_screen
            height = QtToolBox.field_ctrl.size[1] * QtToolBox.field_ctrl.ratio_screen

            painter.drawPixmap(x, y, width, height, self._pixmap)

    @staticmethod
    def get_qt_item(drawing_data_in, screen_ratio=0.1, screen_width=9000, screen_height=6000):
        # TODO - Ajouter la fonctionnalité FOCUS
        # TODO - WARNING - Le flipping des axes n'est pas géré pour le moment et peu impacter les positions rectangles
        draw_data = drawing_data_in.data

        # Calcul de la taille des rectangles
        nb_width, nb_height = draw_data['size']
        ref_x, ref_y = -(screen_width * screen_ratio) / 2, -(screen_height * screen_ratio) / 2
        rect_width = (screen_width * screen_ratio) / nb_width
        rect_height = (screen_height * screen_ratio) / nb_height

        # Création du pinceau
        pen = QtToolBox.create_pen(color=draw_data['grid_color'],
                                   style=draw_data['grid_style'],
                                   width=draw_data['grid_width'],
                                   is_hide=not draw_data['has_grid'])

        # Création de l'objet
        qt_obj = QGraphicsItemGroup()
        qt_obj.setZValue(-5)

        # Parcours de toutes les valeurs des données pour créer un rectangle associé à une valeur
        for nb_line, line in enumerate(draw_data['field_data']):
            for nb_col, case in enumerate(line):
                if case > draw_data['hottest_numb']:
                    case = draw_data['hottest_numb']
                if case < draw_data['coldest_numb']:
                    case = draw_data['coldest_numb']

                # Conversion de la valeur en couleur
                rgb_value = InfluenceMapQtObject._convert_rgb_value_with_minmax(case,
                                                                                draw_data['coldest_numb'],
                                                                                draw_data['hottest_numb'],
                                                                                draw_data['coldest_color'],
                                                                                draw_data['hottest_color'])
                # Création de la brosse
                brush = QtToolBox.create_brush(rgb_value)

                # Création et ajout du rectangle dans le groupe
                qt_obj.addToGroup(QtToolBox.create_rect(ref_x + rect_width * nb_col,
                                                        ref_y + rect_height * nb_line,
                                                        rect_width,
                                                        rect_height,
                                                        pen=pen,
                                                        is_fill=True,
                                                        brush=brush,
                                                        opacity=draw_data['opacity'] / 10.0)
                                  )
        return qt_obj

    @staticmethod
    def _convert_rgb_value_with_minmax(value, value_min, value_max, rgb_min, rgb_max):
        """ Retourne une valeur RGB pour un dégradé de couleur en fonction de la valeur max et min """
        value_r = InfluenceMapQtObject._convert_color_value_with_minmax(value, value_min, value_max, rgb_min[0], rgb_max[0])
        value_g = InfluenceMapQtObject._convert_color_value_with_minmax(value, value_min, value_max, rgb_min[1], rgb_max[1])
        value_b = InfluenceMapQtObject._convert_color_value_with_minmax(value, value_min, value_max, rgb_min[2], rgb_max[2])
        return value_r, value_g, value_b

    @staticmethod
    def _convert_color_value_with_minmax(value, value_min, value_max, color_min, color_max):
        """ Retourne une valeur pour un dégradé de couleur en fonction de la valeur max et min """
        percentage_value = (value - value_min) / (value_max - value_min)
        if color_max > color_min:
            return int((color_max - color_min) * percentage_value + color_min)
        else:
            return int((color_min - color_max) * (1 - percentage_value) + color_max)

    @staticmethod
    def get_datain_associated():
        return DrawInfluenceMapDataIn.__name__
