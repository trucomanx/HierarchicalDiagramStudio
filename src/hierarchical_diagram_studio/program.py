#!/usr/bin/env python3

import sys
import os
import json
import signal
import subprocess
import uuid
import math
from copy import deepcopy
from typing import Optional, List, Dict, Any

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView, QGraphicsScene,
    QGraphicsItem, QGraphicsPathItem, QGraphicsRectItem, QGraphicsEllipseItem,
    QGraphicsTextItem, QGraphicsPolygonItem,
    QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton,
    QToolBar, QAction, QFileDialog, QInputDialog, QMessageBox,
    QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QTextEdit,
    QGraphicsLineItem, QSizePolicy, QMenu, QGraphicsSimpleTextItem,
    QGraphicsDropShadowEffect, QScrollArea
)
from PyQt5.QtCore import (
    Qt, QRectF, QPointF, QSizeF, QLineF, QPoint,
    pyqtSignal, QObject, QUrl
)
from PyQt5.QtGui import (
    QPainter, QPen, QBrush, QColor, QFont, QPainterPath,
    QPolygonF, QTransform, QCursor, QPalette, QKeySequence,
    QLinearGradient, QRadialGradient, QIcon, QDesktopServices
)
from PyQt5.QtSvg import QSvgGenerator
from PyQt5.QtCore import QSize

import hierarchical_diagram_studio.about as about
import hierarchical_diagram_studio.modules.configure as configure 
from hierarchical_diagram_studio.modules.resources import resource_path

from hierarchical_diagram_studio.modules.wabout    import show_about_window
from hierarchical_diagram_studio.desktop import create_desktop_file, create_desktop_directory, create_desktop_menu




# ---------- Path to config file ----------
CONFIG_PATH = os.path.join( os.path.expanduser("~"),
                            ".config", 
                            about.__package__, 
                            "config.json" )

DEFAULT_CONTENT={  

    # TOOLBAR 
    "toolbar_configure": "Configure",
    "toolbar_configure_tooltip": "Open the configure Json file of program GUI",
    "toolbar_about": "About",
    "toolbar_about_tooltip": "About the program",
    "toolbar_coffee": "Coffee",
    "toolbar_coffee_tooltip": "Buy me a coffee (TrucomanX)",
    "toolbar_new": "New",
    "toolbar_new_tooltip": "New diagram (Ctrl+N)",
    "toolbar_open": "Open",
    "toolbar_open_tooltip": "Open .hdiagram file (Ctrl+O)",
    "toolbar_save": "Save",
    "toolbar_save_tooltip": "Save (Ctrl+S)",
    "toolbar_save_as": "Save As",
    "toolbar_save_as_tooltip": "Save as...",
    "toolbar_back": "Back",
    "toolbar_back_tooltip": "Return to previous diagram",
    "toolbar_grid": "Grid",
    "toolbar_fit": "Adjust",
    "toolbar_export_svg": "Export SVG",
    "toolbar_export_svg_tooltip": "Export diagram as SVG image",
    "file_dialog_export_svg_title": "Export as SVG",
    "file_dialog_filter_svg": "SVG Files (*.svg);;All Files (*)",
    "statusbar_svg_exported": "SVG exported: {path}",
    "msg_error_export_svg": "Unable to export SVG:\n{error}",
    "toolbar_export_dot": "Export DOT",
    "toolbar_export_dot_tooltip": "Export diagram as Graphviz .dot file",
    "file_dialog_export_dot_title": "Export as Graphviz DOT",
    "file_dialog_filter_dot": "Graphviz DOT Files (*.dot);;All Files (*)",
    "statusbar_dot_exported": "DOT exported: {path}",
    "msg_error_export_dot": "Unable to export DOT:\n{error}",
    
    # MENU
    "menu_edit_node": "Edit title/summary",
    "menu_add_input": "Add input",
    "menu_remove_input": "Remove last input",
    "menu_add_output": "Add output",
    "menu_remove_output": "Remove last output",
    "menu_open_subdiagram": "Open subdiagram",
    "menu_create_subdiagram": "Create subdiagram",
    "menu_rotate": "Rotate 90°",
    "menu_delete_node": "Delete",
    "menu_add_normal_block": "Add Normal Block",
    "menu_add_merge_block": "Add Merge Block",
    "menu_add_start_block": "Start Block",
    "menu_add_end_block": "End Block",
    "menu_delete_edge": "Delete connection",
    "menu_clear_edge_points": "Clear intermediate points",
    
    # HEADER
    "header_edit_button": "✏ Edit Info",
    "header_no_file": "No file",
    
    # DIALOG
    "dialog_edit_node_title": "Edit Block",
    "dialog_edit_node_label_title": "Title:",
    "dialog_edit_node_label_summary": "Summary:",
    "dialog_edit_diagram_title": "Edit Diagram",
    "dialog_edit_diagram_label_title": "Title:",
    "dialog_edit_diagram_label_summary": "Summary:",
    
    # NODE
    "node_default_title_normal": "Function",
    "node_default_title_merge": "Merge",
    "node_default_title_start": "Start",
    "node_default_title_end": "End",
    "node_new_diagram_title": "New Diagram",
    "node_subdiagram_title_suffix": " -- Subdiagram",
    "node_subdiagram_summary_prefix": "Subdiagram of '",
    "node_subdiagram_summary_suffix": "'",
    
    # MESSAGES
    "msg_save_before_new": "Modified diagram. Do you want to save before creating a new one?",
    "msg_save_before_open": "Diagram modified. Do you want to save before opening?",
    "msg_save_before_exit": "Diagram modified. Do you want to save before exiting?",
    "msg_save_before_subdiagram": "Save current diagram first before creating subdiagram.",
    "msg_save_before_open_sub": "Save the current diagram first.",
    "msg_subdiagram_not_found": "The file '{path}' does not exist.\nDo you want to create a new subdiagram?",
    "msg_subdiagram_created": "Subdiagram created in '{path}'.\nDo you want to navigate to it?",
    "msg_title_save": "Save?",
    "msg_title_exit": "Exit",
    "msg_title_navigate": "Navigate",
    "msg_title_file_not_found": "File not found",
    "msg_title_warning": "Warning",
    "msg_title_error": "Error",
    "msg_error_open_file": "Unable to open file:\n{error}",
    "msg_error_save_file": "Unable to save:\n{error}",
    "msg_error_open_subdiagram": "Unable to open subdiagram:\n{error}",
    "msg_error_create_subdiagram": "Unable to create subdiagram:\n{error}",
    
    # FILE DIALOG
    "file_dialog_open_title": "Open Diagram",
    "file_dialog_save_title": "Save Diagram As",
    "file_dialog_save_sub_title": "Create Subdiagram",
    "file_dialog_filter": "Hierarchical Diagram Files (*.hdiagram);;All Files (*)",
    "file_dialog_filter_hdiagram": "Hierarchical Diagram Files (*.hdiagram)",
    
    # STATUS-BAR
    "statusbar_opened": "Opened: {path}",
    "statusbar_saved": "Saved: {path}",
    "statusbar_returned": "Returned to: {title}",
    "statusbar_navigating": "Navigating to: {title}",
    "statusbar_ready": "Done | Right click on the area to add blocks | Drag ports to connect | F = Fit | Scroll = Zoom",
    
    # WINDOW
    "window_width": 1280,
    "window_height": 720,
    "wiew_min_height": 300,
    "port_radius": 6,
    "port_hit_radius": 10,
    "node_default_width": 140,
    "node_default_height": 70,
    "node_normal_radius": 8,
    "node_merge_radius": 8,
    "node_start_radius": 8,
    "node_end_radius": 8,
    "node_fontsize_title": 9,
    "node_fontsize_summary": 7,
    "node_fontsize_badge": 7,
    "node_fontsize_port": 6,
    "grid_size": 20,
    "edge_hit_tolerance": 8,
    
    # COLORS
    "color_normal_bg": "#2d3748",
    "color_normal_border": "#4a90d9",
    "color_normal_title": "#63b3ed",
    "color_merge_bg": "#2d4a3e",
    "color_merge_border": "#48bb78",
    "color_merge_title": "#68d391",
    "color_start_bg": "#2d3a1e",
    "color_start_border": "#9ae600",
    "color_start_title": "#b5f542",
    "color_end_bg": "#4a1e1e",
    "color_end_border": "#fc8181",
    "color_end_title": "#feb2b2",
    "color_port_input": "#63b3ed",
    "color_port_output": "#f6ad55",
    "color_port_hover": "#ffffff",
    "color_edge": "#a0aec0",
    "color_edge_selected": "#ffd700",
    "color_edge_point": "#ffd700",
    "color_subdiagram": "#9f7aea",
    "color_grid": "#2a2a3e",
    "color_ui_background": "#1a1a2e",
    "color_ui_header": "#1e2433",
    "color_ui_base": "#2d3748",
    "color_ui_neutral": "#4a5568",
    "color_ui_hover": "#63b3ed",
    "color_ui_text": "#e2e8f0",
    "color_ui_highlighted_text": "#ffffff",
    "color_ui_border": "#4a90d9",
}

configure.verify_default_config(CONFIG_PATH,default_content=DEFAULT_CONTENT)

CONFIG=configure.load_config(CONFIG_PATH)

# ============================================================
# CONSTANTS
# ============================================================

PORT_RADIUS = CONFIG["port_radius"]
PORT_HIT_RADIUS = CONFIG["port_hit_radius"]
NODE_DEFAULT_WIDTH = CONFIG["node_default_width"]
NODE_DEFAULT_HEIGHT = CONFIG["node_default_height"]
GRID_SIZE = CONFIG["grid_size"]
EDGE_HIT_TOLERANCE = CONFIG["edge_hit_tolerance"]


# ============================================================
# DATA MODELS
# ============================================================

class Port:
    def __init__(self, name: str, is_input: bool):
        self.name = name
        self.is_input = is_input


class Node:
    NODE_NORMAL = "normal"
    NODE_MERGE = "merge"
    NODE_START = "start"
    NODE_END = "end"

    def __init__(self, node_type: str = NODE_NORMAL, title: str = "Node",
                 summary: str = "", x: float = 0, y: float = 0):
        self.id = str(uuid.uuid4())
        self.type = node_type
        self.title = title
        self.summary = summary
        self.inputs: List[str] = []
        self.outputs: List[str] = []
        self.subdiagram: Optional[str] = None
        self.position = [x, y]
        self.rotation = 0

        # Initialize default ports based on type
        if node_type == Node.NODE_NORMAL:
            self.inputs = ["in"]
            self.outputs = ["out"]
        elif node_type == Node.NODE_MERGE:
            self.inputs = ["in1", "in2"]
            self.outputs = ["out"]
        elif node_type == Node.NODE_START:
            self.inputs = []
            self.outputs = ["out"]
        elif node_type == Node.NODE_END:
            self.inputs = ["in"]
            self.outputs = []

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": self.type,
            "title": self.title,
            "summary": self.summary,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "subdiagram": self.subdiagram,
            "position": self.position,
            "rotation": self.rotation
        }

    @classmethod
    def from_dict(cls, d: Dict) -> "Node":
        n = cls(d.get("type", "normal"), d.get("title", "Node"),
                d.get("summary", ""),
                d["position"][0], d["position"][1])
        n.id = d["id"]
        n.inputs = d.get("inputs", [])
        n.outputs = d.get("outputs", [])
        n.subdiagram = d.get("subdiagram")
        n.rotation = d.get("rotation", 0)
        return n


class Edge:
    def __init__(self, source_node_id: str, source_output_index: int,
                 target_node_id: str, target_input_index: int,
                 points: List[List[float]] = None):
        self.id = str(uuid.uuid4())
        self.source_node_id = source_node_id
        self.source_output_index = source_output_index
        self.target_node_id = target_node_id
        self.target_input_index = target_input_index
        self.points: List[List[float]] = points or []

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "source_node_id": self.source_node_id,
            "source_output_index": self.source_output_index,
            "target_node_id": self.target_node_id,
            "target_input_index": self.target_input_index,
            "points": self.points
        }

    @classmethod
    def from_dict(cls, d: Dict) -> "Edge":
        e = cls(d["source_node_id"], d["source_output_index"],
                d["target_node_id"], d["target_input_index"],
                d.get("points", []))
        e.id = d.get("id", str(uuid.uuid4()))
        return e


class Diagram:
    def __init__(self, title: str = "New Diagram", summary: str = ""):
        self.title = title
        self.summary = summary
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []

    def add_node(self, node: Node):
        self.nodes[node.id] = node

    def remove_node(self, node_id: str):
        self.nodes.pop(node_id, None)
        self.edges = [e for e in self.edges
                      if e.source_node_id != node_id and e.target_node_id != node_id]

    def add_edge(self, edge: Edge):
        self.edges.append(edge)

    def remove_edge(self, edge_id: str):
        self.edges = [e for e in self.edges if e.id != edge_id]

    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "summary": self.summary,
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "edges": [e.to_dict() for e in self.edges]
        }

    @classmethod
    def from_dict(cls, d: Dict) -> "Diagram":
        diagram = cls(d.get("title", "Diagram"), d.get("summary", ""))
        for nd in d.get("nodes", []):
            try:
                node = Node.from_dict(nd)
                diagram.nodes[node.id] = node
            except Exception as ex:
                print(f"Warning: could not load node: {ex}")
        for ed in d.get("edges", []):
            try:
                edge = Edge.from_dict(ed)
                diagram.edges.append(edge)
            except Exception as ex:
                print(f"Warning: could not load edge: {ex}")
        return diagram


# ============================================================
# SERIALIZER
# ============================================================

class DiagramSerializer:
    @staticmethod
    def save(diagram: Diagram, filepath: str):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(diagram.to_dict(), f, indent=2, ensure_ascii=False)

    @staticmethod
    def load(filepath: str) -> Diagram:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return Diagram.from_dict(data)


# ============================================================
# NAVIGATION MANAGER
# ============================================================

class NavigationManager:
    def __init__(self):
        self.stack: List[Dict] = []  # [{"filepath": ..., "diagram": ..., "scene_state": ...}]

    def push(self, filepath: Optional[str], diagram: Diagram, scene_state: Any = None):
        self.stack.append({
            "filepath": filepath,
            "diagram": diagram,
            "scene_state": scene_state
        })

    def pop(self) -> Optional[Dict]:
        if self.can_go_back():
            return self.stack.pop()
        return None

    def can_go_back(self) -> bool:
        return len(self.stack) > 0

    def clear(self):
        self.stack.clear()

    def get_breadcrumb(self, current_title: str) -> List[str]:
        titles = [entry["diagram"].title for entry in self.stack]
        titles.append(current_title)
        return titles


# ============================================================
# GRAPHICS ITEMS
# ============================================================

def get_port_positions(node: Node, rect_width: float, rect_height: float):
    """
    Returns port positions relative to node center (0,0).
    Inputs on left edge, outputs on right edge.
    No manual rotation needed: the QGraphicsItem itself is rotated via setRotation(),
    so child port items rotate automatically with it.
    """
    n_in = len(node.inputs)
    n_out = len(node.outputs)

    hw = rect_width / 2
    hh = rect_height / 2

    input_positions = []
    for i in range(n_in):
        t = 0.5 if n_in == 1 else (i + 1) / (n_in + 1)
        input_positions.append(QPointF(-hw, -hh + t * rect_height))

    output_positions = []
    for i in range(n_out):
        t = 0.5 if n_out == 1 else (i + 1) / (n_out + 1)
        output_positions.append(QPointF(hw, -hh + t * rect_height))

    return input_positions, output_positions


class GraphicsPortItem(QGraphicsEllipseItem):
    def __init__(self, node_item, port_index: int, is_input: bool, parent=None):
        super().__init__(-PORT_RADIUS, -PORT_RADIUS, PORT_RADIUS * 2, PORT_RADIUS * 2, parent)
        self.node_item = node_item
        self.port_index = port_index
        self.is_input = is_input
        self._hovered = False
        self.setAcceptHoverEvents(True)
        self.update_appearance()
        self.setZValue(10)
        self.setCursor(Qt.CrossCursor)

    def update_appearance(self):
        if self._hovered:
            color = QColor(CONFIG["color_port_hover"])
        elif self.is_input:
            color = QColor(CONFIG["color_port_input"])
        else:
            color = QColor(CONFIG["color_port_output"])
        self.setBrush(QBrush(color))
        self.setPen(QPen(Qt.white, 1.5))

    def hoverEnterEvent(self, event):
        self._hovered = True
        self.update_appearance()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self._hovered = False
        self.update_appearance()
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            scene = self.scene()
            if scene:
                scene.start_edge_from_port(self)
        event.accept()

    def scenePos(self) -> QPointF:
        return self.mapToScene(QPointF(0, 0))


class GraphicsNodeItem(QGraphicsItem):
    def __init__(self, node: Node, scene=None):
        super().__init__()
        self.node = node
        self._scene = scene
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setAcceptHoverEvents(True)
        self.setZValue(1)

        # Merge nodes are narrower than normal nodes
        if node.type == Node.NODE_MERGE:
            self.width = int(NODE_DEFAULT_WIDTH * 0.50)
            self.height = int(NODE_DEFAULT_HEIGHT * 2.0)
        else:
            self.width = NODE_DEFAULT_WIDTH
            self.height = NODE_DEFAULT_HEIGHT
        self._hovered = False
        self._port_items: List[GraphicsPortItem] = []

        self.setPos(node.position[0], node.position[1])
        self.setRotation(node.rotation)
        self._rebuild_ports()

    def _rebuild_ports(self):
        for p in self._port_items:
            if p.scene():
                p.scene().removeItem(p)
        self._port_items.clear()

        input_pos, output_pos = get_port_positions(
            self.node, self.width, self.height)

        for i, pos in enumerate(input_pos):
            port = GraphicsPortItem(self, i, True, self)
            port.setPos(pos)
            self._port_items.append(port)

        for i, pos in enumerate(output_pos):
            port = GraphicsPortItem(self, i, False, self)
            port.setPos(pos)
            self._port_items.append(port)

    def get_input_port_item(self, index: int) -> Optional[GraphicsPortItem]:
        for p in self._port_items:
            if p.is_input and p.port_index == index:
                return p
        return None

    def get_output_port_item(self, index: int) -> Optional[GraphicsPortItem]:
        for p in self._port_items:
            if not p.is_input and p.port_index == index:
                return p
        return None

    def get_input_scene_pos(self, index: int) -> QPointF:
        port = self.get_input_port_item(index)
        if port:
            return port.scenePos()
        return self.scenePos()

    def get_output_scene_pos(self, index: int) -> QPointF:
        port = self.get_output_port_item(index)
        if port:
            return port.scenePos()
        return self.scenePos()

    def boundingRect(self) -> QRectF:
        hw = self.width / 2
        hh = self.height / 2
        return QRectF(-hw - PORT_RADIUS - 2, -hh - PORT_RADIUS - 2,
                      hw * 2 + (PORT_RADIUS + 2) * 2,
                      hh * 2 + (PORT_RADIUS + 2) * 2)

    def _get_shape_path(self) -> QPainterPath:
        hw = self.width / 2
        hh = self.height / 2

        path = QPainterPath()
        rect = QRectF(-hw, -hh, hw * 2, hh * 2)
        if self.node.type == Node.NODE_START:
            path.addRoundedRect(rect, CONFIG["node_start_radius"], CONFIG["node_start_radius"])
        elif self.node.type == Node.NODE_END:
            path.addRoundedRect(rect, CONFIG["node_end_radius"], CONFIG["node_end_radius"])
        elif self.node.type == Node.NODE_MERGE:
            path.addRoundedRect(rect, CONFIG["node_merge_radius"], CONFIG["node_merge_radius"])
        else:
            path.addRoundedRect(rect, CONFIG["node_normal_radius"], CONFIG["node_normal_radius"])
        return path

    def paint(self, painter: QPainter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing)

        hw = self.width / 2
        hh = self.height / 2

        # Colors based on type
        t = self.node.type
        
        if t == Node.NODE_NORMAL:
            bg = QColor(CONFIG["color_normal_bg"])
            border = QColor(CONFIG["color_normal_border"])
            title_color = QColor(CONFIG["color_normal_title"])
        elif t == Node.NODE_MERGE:
            bg = QColor(CONFIG["color_merge_bg"])
            border = QColor(CONFIG["color_merge_border"])
            title_color = QColor(CONFIG["color_merge_title"])
        elif t == Node.NODE_START:
            bg = QColor(CONFIG["color_start_bg"])
            border = QColor(CONFIG["color_start_border"])
            title_color = QColor(CONFIG["color_start_title"])
        else:  # END
            bg = QColor(CONFIG["color_end_bg"])
            border = QColor(CONFIG["color_end_border"])
            title_color = QColor(CONFIG["color_end_title"])

        path = self._get_shape_path()

        # Shadow
        if self.isSelected() or self._hovered:
            shadow_pen = QPen(border, 4 if self.isSelected() else 2)
            shadow_pen.setColor(QColor(border.red(), border.green(), border.blue(), 120))
            painter.setPen(shadow_pen)
            painter.drawPath(path)

        # Background gradient
        grad = QLinearGradient(0, -hh, 0, hh)
        grad.setColorAt(0, bg.lighter(120))
        grad.setColorAt(1, bg)
        painter.setBrush(QBrush(grad))
        pen_color = border if not self.isSelected() else QColor(CONFIG["color_edge_selected"])
        pen_width = 2.5 if self.isSelected() else 1.5
        painter.setPen(QPen(pen_color, pen_width))
        painter.drawPath(path)

        # Sub-indicator line (if has subdiagram)
        if self.node.subdiagram and t == Node.NODE_NORMAL:
            painter.setPen(QPen(QColor(CONFIG["color_subdiagram"]), 1.5, Qt.DashLine))
            painter.setBrush(Qt.NoBrush)
            rect_inner = QRectF(-hw + 4, -hh + 4, (hw - 4) * 2, (hh - 4) * 2)

            if t == Node.NODE_START:
                painter.drawRoundedRect(rect_inner, CONFIG["node_start_radius"], CONFIG["node_start_radius"])
            elif t == Node.NODE_END:
                painter.drawRoundedRect(rect_inner, CONFIG["node_end_radius"], CONFIG["node_end_radius"])
            elif t == Node.NODE_MERGE:
                painter.drawRoundedRect(rect_inner, CONFIG["node_merge_radius"], CONFIG["node_merge_radius"])
            else:
                painter.drawRoundedRect(rect_inner, CONFIG["node_normal_radius"], CONFIG["node_normal_radius"])
        
        # Title text
        painter.setPen(QPen(title_color))
        font = QFont("Segoe UI", CONFIG["node_fontsize_title"], QFont.Bold)
        painter.setFont(font)
        title_rect = QRectF(-hw + 8, -hh + 5, (hw - 8) * 2, hh - 5)
        painter.drawText(title_rect, Qt.AlignHCenter | Qt.AlignTop | Qt.TextWordWrap,
                         self.node.title)

        # Summary text (only for normal)
        if self.node.type == Node.NODE_NORMAL and self.node.summary:
            painter.setPen(QPen(QColor(CONFIG["color_ui_text"]).darker(110)))
            font2 = QFont("Segoe UI", CONFIG["node_fontsize_summary"])
            painter.setFont(font2)
            summary_rect = QRectF(-hw + 8, 2, (hw - 8) * 2, hh - 8)
            painter.drawText(summary_rect, Qt.AlignHCenter | Qt.AlignTop | Qt.TextWordWrap,
                             self.node.summary)

        # Type badge
        if t == Node.NODE_NORMAL:
            type_text = "FN"
        elif t == Node.NODE_MERGE:
            type_text = "MRG"
        elif t == Node.NODE_START:
            type_text = "▶"
        else:
            type_text = "■"

        painter.setPen(QPen(title_color.darker(110)))
        font3 = QFont("Segoe UI", CONFIG["node_fontsize_badge"])
        painter.setFont(font3)
        badge_rect = QRectF(hw - 26, hh - 16, 22, 12)
        painter.drawText(badge_rect, Qt.AlignRight | Qt.AlignBottom, type_text)

        # Port labels
        input_pos, output_pos = get_port_positions(self.node, self.width, self.height)
        font4 = QFont("Segoe UI", CONFIG["node_fontsize_port"])
        painter.setFont(font4)
        for i, pos in enumerate(input_pos):
            if i < len(self.node.inputs):
                lbl = self.node.inputs[i]
                painter.setPen(QPen(QColor(CONFIG["color_port_input"]).lighter(130)))
                lr = QRectF(pos.x() + PORT_RADIUS + 2, pos.y() - 8, 40, 16)
                painter.drawText(lr, Qt.AlignLeft | Qt.AlignVCenter, lbl)
        for i, pos in enumerate(output_pos):
            if i < len(self.node.outputs):
                lbl = self.node.outputs[i]
                painter.setPen(QPen(QColor(CONFIG["color_port_output"]).lighter(130)))
                lr = QRectF(pos.x() - 42 - PORT_RADIUS, pos.y() - 8, 40, 16)
                painter.drawText(lr, Qt.AlignRight | Qt.AlignVCenter, lbl)

    def hoverEnterEvent(self, event):
        self._hovered = True
        self.update()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self._hovered = False
        self.update()
        super().hoverLeaveEvent(event)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            self.node.position = [self.pos().x(), self.pos().y()]
            if self._scene:
                self._scene.update_edges_for_node(self.node.id)
        return super().itemChange(change, value)

    def contextMenuEvent(self, event):
        menu = QMenu()
        t = self.node.type

        if t in (Node.NODE_NORMAL, Node.NODE_START, Node.NODE_END):
            act_edit = menu.addAction(QIcon.fromTheme("document-edit"), CONFIG["menu_edit_node"])
            act_edit.triggered.connect(self._edit_title_summary)

        if t == Node.NODE_NORMAL:
            menu.addSeparator()
            act_ai = menu.addAction(QIcon.fromTheme("list-add"), CONFIG["menu_add_input"])
            act_ai.triggered.connect(self._add_input)
            act_ri = menu.addAction(QIcon.fromTheme("list-remove"), CONFIG["menu_remove_input"])
            act_ri.triggered.connect(self._remove_input)
            act_ao = menu.addAction(QIcon.fromTheme("list-add"), CONFIG["menu_add_output"])
            act_ao.triggered.connect(self._add_output)
            act_ro = menu.addAction(QIcon.fromTheme("list-remove"), CONFIG["menu_remove_output"])
            act_ro.triggered.connect(self._remove_output)
            menu.addSeparator()
            if self.node.subdiagram:
                act_open = menu.addAction(QIcon.fromTheme("document-open"), CONFIG["menu_open_subdiagram"])
                act_open.triggered.connect(self._open_subdiagram)
            else:
                act_create = menu.addAction(QIcon.fromTheme("document-new"), CONFIG["menu_create_subdiagram"])
                act_create.triggered.connect(self._create_subdiagram)

        if t == Node.NODE_MERGE:
            menu.addSeparator()
            act_ai = menu.addAction(QIcon.fromTheme("list-add"), CONFIG["menu_add_input"])
            act_ai.triggered.connect(self._add_input)
            act_ri = menu.addAction(QIcon.fromTheme("list-remove"), CONFIG["menu_remove_input"])
            act_ri.triggered.connect(self._remove_input)

        menu.addSeparator()
        act_rot = menu.addAction(QIcon.fromTheme("object-rotate-right"), CONFIG["menu_rotate"])
        act_rot.triggered.connect(self._rotate)
        menu.addSeparator()
        act_del = menu.addAction(QIcon.fromTheme("edit-delete"), CONFIG["menu_delete_node"])
        act_del.triggered.connect(self._delete)

        menu.exec_(event.screenPos())

    def _edit_title_summary(self):
        dlg = EditNodeDialog(self.node.title, self.node.summary,
                             self.node.type in (Node.NODE_NORMAL,))
        if dlg.exec_() == QDialog.Accepted:
            self.node.title = dlg.title_edit.text().strip() or self.node.title
            self.node.summary = dlg.summary_edit.toPlainText().strip()
            self.update()

    def _add_input(self):
        if self.node.type == Node.NODE_START:
            return
        idx = len(self.node.inputs) + 1
        self.node.inputs.append(f"in{idx}")
        self._rebuild_ports()
        self.update()

    def _remove_input(self):
        if self.node.type in (Node.NODE_END,) and len(self.node.inputs) <= 1:
            return
        if self.node.type == Node.NODE_MERGE and len(self.node.inputs) <= 1:
            return
        if self.node.inputs:
            removed_idx = len(self.node.inputs) - 1
            self.node.inputs.pop()
            if self._scene:
                self._scene.remove_edges_for_port(self.node.id, removed_idx, True)
            self._rebuild_ports()
            self.update()

    def _add_output(self):
        if self.node.type in (Node.NODE_MERGE, Node.NODE_END):
            return
        idx = len(self.node.outputs) + 1
        self.node.outputs.append(f"out{idx}")
        self._rebuild_ports()
        self.update()

    def _remove_output(self):
        if self.node.type in (Node.NODE_MERGE, Node.NODE_START) and len(self.node.outputs) <= 1:
            return
        if self.node.outputs:
            removed_idx = len(self.node.outputs) - 1
            self.node.outputs.pop()
            if self._scene:
                self._scene.remove_edges_for_port(self.node.id, removed_idx, False)
            self._rebuild_ports()
            self.update()

    def _rotate(self):
        self.node.rotation = (self.node.rotation + 90) % 360
        self.setRotation(self.node.rotation)
        self._rebuild_ports()
        self.prepareGeometryChange()
        self.update()
        if self._scene:
            self._scene.update_edges_for_node(self.node.id)

    def _delete(self):
        if self._scene:
            self._scene.remove_node_item(self)

    def _create_subdiagram(self):
        if self._scene and hasattr(self._scene, 'main_window'):
            self._scene.main_window.create_subdiagram_for_node(self)

    def _open_subdiagram(self):
        if self._scene and hasattr(self._scene, 'main_window'):
            self._scene.main_window.open_subdiagram_for_node(self)

    def mouseDoubleClickEvent(self, event):
        if self.node.type == Node.NODE_NORMAL:
            if self.node.subdiagram:
                self._open_subdiagram()
            else:
                self._edit_title_summary()
        else:
            self._edit_title_summary()


class EdgePoint:
    """Represents a draggable intermediate point on an edge."""
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def pos(self) -> QPointF:
        return QPointF(self.x, self.y)


class GraphicsEdgeItem(QGraphicsPathItem):
    def __init__(self, edge: Edge, scene=None):
        super().__init__()
        self.edge = edge
        self._scene = scene
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setAcceptHoverEvents(True)
        self.setZValue(0)
        self._hovered = False
        self._dragging_point_idx: Optional[int] = None
        self._drag_offset = QPointF()
        self.setCursor(Qt.ArrowCursor)
        self._update_pen()

    def _update_pen(self):
        if self.isSelected() or self._hovered:
            color = QColor(CONFIG["color_edge_selected"])
            width = 2.5
        else:
            color = QColor(CONFIG["color_edge"])
            width = 1.5
        pen = QPen(color, width)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        self.setPen(pen)

    def set_endpoints(self, source_pos: QPointF, target_pos: QPointF):
        self._source_pos = source_pos
        self._target_pos = target_pos
        self._rebuild_path()

    def _rebuild_path(self):
        if not hasattr(self, '_source_pos'):
            return
        path = QPainterPath()
        all_points = [self._source_pos] + \
                     [QPointF(p[0], p[1]) for p in self.edge.points] + \
                     [self._target_pos]

        if len(all_points) < 2:
            return

        path.moveTo(all_points[0])
        for i in range(1, len(all_points)):
            path.lineTo(all_points[i])

        self.setPath(path)

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing)
        self._update_pen()
        painter.setPen(self.pen())
        painter.drawPath(self.path())

        # Draw arrow at endpoint
        if hasattr(self, '_target_pos') and hasattr(self, '_source_pos'):
            all_points = [self._source_pos] + \
                         [QPointF(p[0], p[1]) for p in self.edge.points] + \
                         [self._target_pos]
            if len(all_points) >= 2:
                p1 = all_points[-2]
                p2 = all_points[-1]
                self._draw_arrow(painter, p1, p2)

        # Draw intermediate points
        if self.isSelected() or self._hovered:
            painter.setBrush(QBrush(QColor(CONFIG["color_edge_point"])))
            painter.setPen(QPen(Qt.black, 1))
            for pt in self.edge.points:
                painter.drawEllipse(QPointF(pt[0], pt[1]), 5, 5)

    def _draw_arrow(self, painter, p1: QPointF, p2: QPointF):
        dx = p2.x() - p1.x()
        dy = p2.y() - p1.y()
        length = math.sqrt(dx * dx + dy * dy)
        if length < 1:
            return
        nx, ny = dx / length, dy / length
        arrow_len = 12
        arrow_width = 6
        base = QPointF(p2.x() - nx * arrow_len, p2.y() - ny * arrow_len)
        left = QPointF(base.x() - ny * arrow_width, base.y() + nx * arrow_width)
        right = QPointF(base.x() + ny * arrow_width, base.y() - nx * arrow_width)
        color = QColor(CONFIG["color_edge_selected"]) if (self.isSelected() or self._hovered) else QColor(CONFIG["color_edge"])
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(color, 1))
        poly = QPolygonF([p2, left, right])
        painter.drawPolygon(poly)

    def boundingRect(self) -> QRectF:
        br = super().boundingRect()
        return br.adjusted(-10, -10, 10, 10)

    def shape(self) -> QPainterPath:
        # Make edge easier to click
        stroker = QPainterPath()
        if self.path().isEmpty():
            return stroker
        from PyQt5.QtGui import QPainterPathStroker
        ps = QPainterPathStroker()
        ps.setWidth(EDGE_HIT_TOLERANCE * 2)
        return ps.createStroke(self.path())

    def hoverEnterEvent(self, event):
        self._hovered = True
        self.setCursor(Qt.PointingHandCursor)
        self.update()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self._hovered = False
        self.setCursor(Qt.ArrowCursor)
        self.update()
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos = event.pos()
            scene_pos = event.scenePos()

            # Check if clicking near an intermediate point
            for i, pt in enumerate(self.edge.points):
                d = math.sqrt((scene_pos.x() - pt[0]) ** 2 + (scene_pos.y() - pt[1]) ** 2)
                if d < 10:
                    self._dragging_point_idx = i
                    self._drag_offset = QPointF(scene_pos.x() - pt[0], scene_pos.y() - pt[1])
                    event.accept()
                    return

            # Insert new intermediate point
            click_pos = event.scenePos()
            self._insert_point_near(click_pos)
            event.accept()
        elif event.button() == Qt.RightButton:
            self._context_menu(event)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._dragging_point_idx is not None:
            sp = event.scenePos()
            self.edge.points[self._dragging_point_idx] = [
                sp.x() - self._drag_offset.x(),
                sp.y() - self._drag_offset.y()
            ]
            if self._scene:
                self._scene.refresh_edge(self)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._dragging_point_idx = None
        super().mouseReleaseEvent(event)

    def _insert_point_near(self, click_pos: QPointF):
        if not hasattr(self, '_source_pos'):
            return
        all_pts = [self._source_pos] + \
                  [QPointF(p[0], p[1]) for p in self.edge.points] + \
                  [self._target_pos]

        best_idx = 0
        best_dist = float('inf')
        for i in range(len(all_pts) - 1):
            p1, p2 = all_pts[i], all_pts[i + 1]
            d = self._point_to_segment_dist(click_pos, p1, p2)
            if d < best_dist:
                best_dist = d
                best_idx = i

        # Insert after best_idx (which is into edge.points array)
        self.edge.points.insert(best_idx, [click_pos.x(), click_pos.y()])
        if self._scene:
            self._scene.refresh_edge(self)

    def _point_to_segment_dist(self, p: QPointF, a: QPointF, b: QPointF) -> float:
        ax, ay = a.x(), a.y()
        bx, by = b.x(), b.y()
        px, py = p.x(), p.y()
        dx, dy = bx - ax, by - ay
        if dx == 0 and dy == 0:
            return math.sqrt((px - ax) ** 2 + (py - ay) ** 2)
        t = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)
        t = max(0, min(1, t))
        nearest_x = ax + t * dx
        nearest_y = ay + t * dy
        return math.sqrt((px - nearest_x) ** 2 + (py - nearest_y) ** 2)

    def _context_menu(self, event):
        menu = QMenu()
        act_del = menu.addAction(QIcon.fromTheme("edit-delete"), CONFIG["menu_delete_edge"])
        act_del.triggered.connect(self._delete)
        act_clr = menu.addAction(QIcon.fromTheme("edit-clear"), CONFIG["menu_clear_edge_points"])
        act_clr.triggered.connect(self._clear_points)
        menu.exec_(event.screenPos())

    def _delete(self):
        if self._scene:
            self._scene.remove_edge_item(self)

    def _clear_points(self):
        self.edge.points.clear()
        if self._scene:
            self._scene.refresh_edge(self)


# ============================================================
# DIAGRAM SCENE
# ============================================================

class TempEdgeLine(QGraphicsPathItem):
    """Visual feedback while drawing a new edge."""
    def __init__(self):
        super().__init__()
        pen = QPen(QColor(CONFIG["color_port_output"]), 2, Qt.DashLine)
        self.setPen(pen)
        self.setZValue(100)

    def update_path(self, start: QPointF, end: QPointF):
        path = QPainterPath()
        path.moveTo(start)
        # Simple bezier
        mid_x = (start.x() + end.x()) / 2
        ctrl1 = QPointF(mid_x, start.y())
        ctrl2 = QPointF(mid_x, end.y())
        path.cubicTo(ctrl1, ctrl2, end)
        self.setPath(path)


class DiagramScene(QGraphicsScene):
    diagram_changed = pyqtSignal()

    def __init__(self, diagram: Diagram, main_window=None):
        super().__init__()
        self.diagram = diagram
        self.main_window = main_window
        self.setBackgroundBrush(QBrush(QColor(CONFIG["color_ui_background"])))

        self._node_items: Dict[str, GraphicsNodeItem] = {}
        self._edge_items: Dict[str, GraphicsEdgeItem] = {}

        # Edge drawing state
        self._drawing_edge = False
        self._edge_source_port: Optional[GraphicsPortItem] = None
        self._temp_edge_line: Optional[TempEdgeLine] = None

        # Load existing diagram
        self._load_diagram()

    def _load_diagram(self):
        for node in self.diagram.nodes.values():
            self._add_node_item(node)
        for edge in self.diagram.edges:
            self._add_edge_item(edge)

    def _add_node_item(self, node: Node) -> GraphicsNodeItem:
        item = GraphicsNodeItem(node, self)
        self.addItem(item)
        self._node_items[node.id] = item
        return item

    def _add_edge_item(self, edge: Edge) -> Optional[GraphicsEdgeItem]:
        src_item = self._node_items.get(edge.source_node_id)
        tgt_item = self._node_items.get(edge.target_node_id)
        if not src_item or not tgt_item:
            return None

        edge_item = GraphicsEdgeItem(edge, self)
        self.addItem(edge_item)
        self._edge_items[edge.id] = edge_item

        src_pos = src_item.get_output_scene_pos(edge.source_output_index)
        tgt_pos = tgt_item.get_input_scene_pos(edge.target_input_index)
        edge_item.set_endpoints(src_pos, tgt_pos)
        return edge_item

    def add_new_node(self, node_type: str, pos: QPointF):
        titles = {
            Node.NODE_NORMAL: CONFIG["node_default_title_normal"],
            Node.NODE_MERGE:  CONFIG["node_default_title_merge"],
            Node.NODE_START:  CONFIG["node_default_title_start"],
            Node.NODE_END:    CONFIG["node_default_title_end"]
        }
        node = Node(node_type, titles.get(node_type, "Node"), "", pos.x(), pos.y())
        self.diagram.add_node(node)
        item = self._add_node_item(node)
        self.diagram_changed.emit()
        return item

    def remove_node_item(self, item: GraphicsNodeItem):
        node_id = item.node.id
        # Remove connected edges
        edges_to_remove = [e for e in self._edge_items.values()
                           if e.edge.source_node_id == node_id or e.edge.target_node_id == node_id]
        for e in edges_to_remove:
            self.remove_edge_item(e)
        # Remove node
        self.removeItem(item)
        del self._node_items[node_id]
        self.diagram.remove_node(node_id)
        self.diagram_changed.emit()

    def remove_edge_item(self, item: GraphicsEdgeItem):
        edge_id = item.edge.id
        self.removeItem(item)
        if edge_id in self._edge_items:
            del self._edge_items[edge_id]
        self.diagram.remove_edge(edge_id)
        self.diagram_changed.emit()

    def remove_edges_for_port(self, node_id: str, port_index: int, is_input: bool):
        to_remove = []
        for eid, eitem in self._edge_items.items():
            edge = eitem.edge
            if is_input and edge.target_node_id == node_id and edge.target_input_index == port_index:
                to_remove.append(eitem)
            elif not is_input and edge.source_node_id == node_id and edge.source_output_index == port_index:
                to_remove.append(eitem)
        for eitem in to_remove:
            self.remove_edge_item(eitem)

    def update_edges_for_node(self, node_id: str):
        node_item = self._node_items.get(node_id)
        if not node_item:
            return
        for edge_item in self._edge_items.values():
            edge = edge_item.edge
            if edge.source_node_id == node_id:
                src_pos = node_item.get_output_scene_pos(edge.source_output_index)
                tgt_item = self._node_items.get(edge.target_node_id)
                tgt_pos = tgt_item.get_input_scene_pos(edge.target_input_index) if tgt_item else src_pos
                edge_item.set_endpoints(src_pos, tgt_pos)
            elif edge.target_node_id == node_id:
                tgt_pos = node_item.get_input_scene_pos(edge.target_input_index)
                src_item = self._node_items.get(edge.source_node_id)
                src_pos = src_item.get_output_scene_pos(edge.source_output_index) if src_item else tgt_pos
                edge_item.set_endpoints(src_pos, tgt_pos)

    def refresh_edge(self, edge_item: GraphicsEdgeItem):
        edge = edge_item.edge
        src_item = self._node_items.get(edge.source_node_id)
        tgt_item = self._node_items.get(edge.target_node_id)
        if src_item and tgt_item:
            src_pos = src_item.get_output_scene_pos(edge.source_output_index)
            tgt_pos = tgt_item.get_input_scene_pos(edge.target_input_index)
            edge_item.set_endpoints(src_pos, tgt_pos)

    def start_edge_from_port(self, port: GraphicsPortItem):
        if port.is_input:
            return  # Only start from output ports
        self._drawing_edge = True
        self._edge_source_port = port
        if self._temp_edge_line:
            self.removeItem(self._temp_edge_line)
        self._temp_edge_line = TempEdgeLine()
        self.addItem(self._temp_edge_line)
        start_pos = port.scenePos()
        self._temp_edge_line.update_path(start_pos, start_pos)

    def mouseMoveEvent(self, event):
        if self._drawing_edge and self._temp_edge_line and self._edge_source_port:
            start_pos = self._edge_source_port.scenePos()
            self._temp_edge_line.update_path(start_pos, event.scenePos())
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        if self._drawing_edge:
            # Find a port under mouse
            items = self.items(event.scenePos())
            target_port = None
            for item in items:
                if isinstance(item, GraphicsPortItem) and item.is_input:
                    target_port = item
                    break

            if target_port:
                self._finish_edge(target_port)
            else:
                self._cancel_edge()
            event.accept()
            return

        super().mousePressEvent(event)

    def _finish_edge(self, target_port: GraphicsPortItem):
        if not self._edge_source_port:
            return
        src_port = self._edge_source_port
        src_node = src_port.node_item.node
        tgt_node = target_port.node_item.node

        # Avoid self-connections
        if src_node.id == tgt_node.id:
            self._cancel_edge()
            return

        edge = Edge(src_node.id, src_port.port_index,
                    tgt_node.id, target_port.port_index)
        self.diagram.add_edge(edge)
        self._add_edge_item(edge)
        self._cancel_edge()
        self.diagram_changed.emit()

    def _cancel_edge(self):
        self._drawing_edge = False
        self._edge_source_port = None
        if self._temp_edge_line:
            self.removeItem(self._temp_edge_line)
            self._temp_edge_line = None

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            if self._drawing_edge:
                self._cancel_edge()
                return
        if event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
            selected = self.selectedItems()
            for item in selected:
                if isinstance(item, GraphicsNodeItem):
                    self.remove_node_item(item)
                elif isinstance(item, GraphicsEdgeItem):
                    self.remove_edge_item(item)
        super().keyPressEvent(event)

    def contextMenuEvent(self, event):
        items = self.items(event.scenePos())
        if not items:
            # Background context menu - add new nodes
            menu = QMenu()
            pos = event.scenePos()
            act_normal = menu.addAction(QIcon.fromTheme("list-add"), CONFIG["menu_add_normal_block"])
            act_merge = menu.addAction(QIcon.fromTheme("list-add"), CONFIG["menu_add_merge_block"])
            act_start = menu.addAction(QIcon.fromTheme("media-playback-start"), CONFIG["menu_add_start_block"])
            act_end = menu.addAction(QIcon.fromTheme("media-playback-stop"), CONFIG["menu_add_end_block"])

            act_normal.triggered.connect(lambda: self.add_new_node(Node.NODE_NORMAL, pos))
            act_merge.triggered.connect(lambda: self.add_new_node(Node.NODE_MERGE, pos))
            act_start.triggered.connect(lambda: self.add_new_node(Node.NODE_START, pos))
            act_end.triggered.connect(lambda: self.add_new_node(Node.NODE_END, pos))

            menu.exec_(event.screenPos())
        else:
            super().contextMenuEvent(event)

    def drawBackground(self, painter: QPainter, rect: QRectF):
        super().drawBackground(painter, rect)
        # Draw grid
        if hasattr(self, 'show_grid') and self.show_grid:
            painter.setPen(QPen(QColor(CONFIG["color_grid"]), 0.5))
            left = int(rect.left()) - (int(rect.left()) % GRID_SIZE)
            top = int(rect.top()) - (int(rect.top()) % GRID_SIZE)
            x = left
            while x < rect.right():
                painter.drawLine(int(x), int(rect.top()), int(x), int(rect.bottom()))
                x += GRID_SIZE
            y = top
            while y < rect.bottom():
                painter.drawLine(int(rect.left()), int(y), int(rect.right()), int(y))
                y += GRID_SIZE

    show_grid: bool = True


# ============================================================
# GRAPHICS VIEW
# ============================================================

class DiagramView(QGraphicsView):
    def __init__(self, scene: DiagramScene = None):
        super().__init__(scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self._pan_active = False
        self._pan_start = QPoint()
        self.setStyleSheet("QGraphicsView { border: none; background: transparent; }")

    def wheelEvent(self, event):
        factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        self.scale(factor, factor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self._pan_active = True
            self._pan_start = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._pan_active:
            delta = event.pos() - self._pan_start
            self._pan_start = event.pos()
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y())
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self._pan_active = False
            self.setCursor(Qt.ArrowCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F:
            self.fit_in_view()
        elif event.key() == Qt.Key_Plus or event.key() == Qt.Key_Equal:
            self.scale(1.2, 1.2)
        elif event.key() == Qt.Key_Minus:
            self.scale(1 / 1.2, 1 / 1.2)
        else:
            super().keyPressEvent(event)

    def fit_in_view(self):
        if self.scene():
            br = self.scene().itemsBoundingRect()
            if not br.isEmpty():
                self.fitInView(br.adjusted(-50, -50, 50, 50), Qt.KeepAspectRatio)


# ============================================================
# DIALOGS
# ============================================================

class EditNodeDialog(QDialog):
    def __init__(self, title: str, summary: str, show_summary: bool = True):
        super().__init__()
        self.setWindowTitle(CONFIG["dialog_edit_node_title"])
        self.setMinimumWidth(400)
        self.setMinimumHeight(250)

        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        main_layout.addLayout(form_layout)

        self.title_edit = QLineEdit(title)
        form_layout.addRow(CONFIG["dialog_edit_node_label_title"], self.title_edit)

        self.summary_edit = QTextEdit()
        self.summary_edit.setPlainText(summary)
        self.summary_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        if show_summary:
            form_layout.addRow(CONFIG["dialog_edit_node_label_summary"], self.summary_edit)
            main_layout.setStretchFactor(form_layout, 1)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)

        self.setStyleSheet(f"""
QDialog {{ 
    background: {CONFIG['color_ui_base']}; 
    color: {CONFIG['color_ui_text']}; 
}}

QLineEdit, QTextEdit {{ 
    background: {CONFIG['color_ui_background']}; 
    color: {CONFIG['color_ui_text']};
    border: 1px solid {CONFIG['color_ui_border']}; 
    border-radius: 4px;
    padding: 4px; 
}}

QLabel {{ 
    color: {CONFIG['color_edge']}; 
}}

QPushButton {{ 
    background: {CONFIG['color_ui_border']}; 
    color: white; 
    border-radius: 4px;
    padding: 6px 16px; 
    border: none; 
}}

QPushButton:hover {{ 
    background: {CONFIG['color_ui_hover']}; 
}}
        """)


class EditDiagramDialog(QDialog):
    def __init__(self, title: str, summary: str):
        super().__init__()
        self.setWindowTitle(CONFIG["dialog_edit_diagram_title"])
        self.setMinimumWidth(450)
        self.setMinimumHeight(280)

        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        main_layout.addLayout(form_layout)

        self.title_edit = QLineEdit(title)
        form_layout.addRow(CONFIG["dialog_edit_diagram_label_title"], self.title_edit)

        self.summary_edit = QTextEdit()
        self.summary_edit.setPlainText(summary)
        self.summary_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        form_layout.addRow(CONFIG["dialog_edit_diagram_label_summary"], self.summary_edit)
        main_layout.setStretchFactor(form_layout, 1)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)

        self.setStyleSheet(f"""
QDialog {{ 
    background: {CONFIG['color_ui_base']}; 
    color: {CONFIG['color_ui_text']}; 
}}

QLineEdit, QTextEdit {{ 
    background: {CONFIG['color_ui_background']}; 
    color: {CONFIG['color_ui_text']};
    border: 1px solid {CONFIG['color_ui_border']}; 
    border-radius: 4px;
    padding: 4px; 
}}

QLabel {{ 
    color: {CONFIG['color_edge']}; 
}}

QPushButton {{ 
    background: {CONFIG['color_ui_border']}; 
    color: white; 
    border-radius: 4px;
    padding: 6px 16px; 
    border: none; 
}}

QPushButton:hover {{ 
    background: {CONFIG['color_ui_hover']}; 
}}
        """)


# ============================================================
# MAIN WINDOW
# ============================================================

STYLE_SHEET = f"""
QMainWindow {{ background: {CONFIG['color_ui_background']}; }}
QWidget {{
    background: {CONFIG['color_ui_background']}; 
    color: {CONFIG['color_ui_text']}; 
    font-family: 'Segoe UI', Arial, sans-serif; 
}}

QPushButton {{
    background: {CONFIG['color_ui_base']};
    color: {CONFIG['color_edge']};
    border: 1px solid {CONFIG['color_ui_neutral']};
    border-radius: 5px;
    padding: 5px 12px;
    font-size: 12px;
}}

QPushButton:hover {{
    background: {CONFIG['color_ui_neutral']};
    color: {CONFIG['color_ui_text']};
}}

QPushButton:pressed {{
    background: {CONFIG['color_ui_border']};
    color: white;
}}

QPushButton:disabled {{
    color: {CONFIG['color_ui_neutral']};
    border-color: {CONFIG['color_ui_base']};
}}

QToolBar {{
    background: {CONFIG['color_ui_header']};
    border-bottom: 1px solid {CONFIG['color_ui_base']};
    spacing: 4px;
    padding: 4px;
}}

QLabel {{ background: transparent; }}

QScrollBar:vertical {{
    background: {CONFIG['color_ui_background']};
    width: 8px;
}}

QScrollBar::handle:vertical {{
    background: {CONFIG['color_ui_neutral']};
    border-radius: 4px;
}}

QScrollBar:horizontal {{
    background: {CONFIG['color_ui_background']};
    height: 8px;
}}

QScrollBar::handle:horizontal {{
    background: {CONFIG['color_ui_neutral']};
    border-radius: 4px;
}}

QMenu {{
    background: {CONFIG['color_ui_base']};
    border: 1px solid {CONFIG['color_ui_neutral']};
    color: {CONFIG['color_ui_text']};
    padding: 4px;
}}

QMenu::item:selected {{
    background: {CONFIG['color_ui_border']};
    border-radius: 3px;
}}

QMenu::separator {{
    height: 1px;
    background: {CONFIG['color_ui_neutral']};
    margin: 3px 0;
}}
"""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(about.__program_name__)
        self.resize(CONFIG["window_width"], CONFIG["window_height"])
        
        self.setStyleSheet(STYLE_SHEET)
        
        ## Icon
        # Get base directory for icons
        self.icon_path = resource_path("icons", "logo.png")
        self.setWindowIcon(QIcon(self.icon_path)) 

        self.current_filepath: Optional[str] = None
        self.current_diagram: Diagram = Diagram(CONFIG["node_new_diagram_title"], "")
        self.nav_manager = NavigationManager()
        self._modified = False

        self._setup_ui()
        self._new_scene(self.current_diagram)
        self._update_header()
        self._update_breadcrumb()
        self._update_back_button()

    def _setup_ui(self):
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Toolbar
        toolbar = self._build_toolbar()
        main_layout.addWidget(toolbar)

        # Header section
        header = self._build_header()
        main_layout.addWidget(header)

        # Divider
        divider = QWidget()
        divider.setFixedHeight(1)
        divider.setStyleSheet(f"background: {CONFIG['color_ui_base']};")
        main_layout.addWidget(divider)

        # Graphics view
        self.view = DiagramView()
        self.view.setMinimumHeight(CONFIG["wiew_min_height"])
        main_layout.addWidget(self.view, 1)

        # Status bar
        self.statusBar().setStyleSheet(f"background: {CONFIG['color_ui_header']}; color: {CONFIG['color_ui_text']}; font-size: 11px;")
        self.statusBar().showMessage(CONFIG["statusbar_ready"])

    def _build_toolbar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(44)
        bar.setStyleSheet(f"background: {CONFIG['color_ui_header']}; border-bottom: 1px solid {CONFIG['color_ui_base']};")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(6)

        def btn(theme_icon: str, fallback_text: str, tip: str, cb) -> QPushButton:
            b = QPushButton(fallback_text)
            icon = QIcon.fromTheme(theme_icon)
            if not icon.isNull():
                b.setIcon(icon)
                b.setText(fallback_text)
            b.setToolTip(tip)
            b.clicked.connect(cb)
            b.setFixedHeight(32)
            b.setIconSize(QSize(16, 16))
            return b

        self.btn_new     = btn("document-new",      CONFIG["toolbar_new"],     CONFIG["toolbar_new_tooltip"],     self.action_new)
        self.btn_open    = btn("document-open",     CONFIG["toolbar_open"],    CONFIG["toolbar_open_tooltip"],    self.action_open)
        self.btn_save    = btn("document-save",     CONFIG["toolbar_save"],    CONFIG["toolbar_save_tooltip"],    self.action_save)
        self.btn_save_as = btn("document-save-as",  CONFIG["toolbar_save_as"], CONFIG["toolbar_save_as_tooltip"], self.action_save_as)
        self.btn_export_svg = btn("image-x-generic", CONFIG["toolbar_export_svg"], CONFIG["toolbar_export_svg_tooltip"], self.action_export_svg)
        self.btn_export_dot = btn("text-x-generic",  CONFIG["toolbar_export_dot"], CONFIG["toolbar_export_dot_tooltip"], self.action_export_dot)

        layout.addWidget(self.btn_new)
        layout.addWidget(self.btn_open)
        layout.addWidget(self.btn_save)
        layout.addWidget(self.btn_save_as)
        layout.addWidget(self.btn_export_svg)
        layout.addWidget(self.btn_export_dot)

        # Separator
        sep = QWidget()
        sep.setFixedWidth(1)
        sep.setFixedHeight(24)
        sep.setStyleSheet("background: {CONFIG['color_ui_neutral']};")
        layout.addWidget(sep)

        self.btn_back = btn("go-previous", CONFIG["toolbar_back"], CONFIG["toolbar_back_tooltip"], self.action_back)
        self.btn_back.setEnabled(False)
        layout.addWidget(self.btn_back)

        layout.addStretch()

        # Grid toggle
        self.btn_grid = QPushButton(CONFIG["toolbar_grid"])
        grid_icon = QIcon.fromTheme("view-grid")
        if not grid_icon.isNull():
            self.btn_grid.setIcon(grid_icon)
        self.btn_grid.setCheckable(True)
        self.btn_grid.setChecked(True)
        self.btn_grid.setFixedHeight(32)
        self.btn_grid.clicked.connect(self._toggle_grid)
        layout.addWidget(self.btn_grid)

        # Fit view
        btn_fit = QPushButton(CONFIG["toolbar_fit"])
        fit_icon = QIcon.fromTheme("zoom-fit-best")
        if not fit_icon.isNull():
            btn_fit.setIcon(fit_icon)
        btn_fit.setFixedHeight(32)
        btn_fit.clicked.connect(lambda: self.view.fit_in_view())
        layout.addWidget(btn_fit)

        # Configure
        btn_configure = QPushButton(CONFIG["toolbar_configure"])
        configure_icon = QIcon.fromTheme("document-properties")
        if not configure_icon.isNull():
            btn_configure.setIcon(configure_icon)
        btn_configure.setFixedHeight(32)
        btn_configure.clicked.connect(lambda: self.open_configure_editor())
        layout.addWidget(btn_configure)

        # Coffee
        btn_coffee = QPushButton(CONFIG["toolbar_coffee"])
        coffee_icon = QIcon.fromTheme("emblem-favorite")
        if not coffee_icon.isNull():
            btn_coffee.setIcon(coffee_icon)
        btn_coffee.setFixedHeight(32)
        btn_coffee.clicked.connect(lambda: self.on_coffee_action_click())
        layout.addWidget(btn_coffee)

        # About
        btn_about = QPushButton(CONFIG["toolbar_about"])
        about_icon = QIcon.fromTheme("help-about")
        if not about_icon.isNull():
            btn_about.setIcon(about_icon)
        btn_about.setFixedHeight(32)
        btn_about.clicked.connect(lambda: self.open_about())
        layout.addWidget(btn_about)

        # Keyboard shortcuts
        from PyQt5.QtWidgets import QShortcut
        QShortcut(QKeySequence("Ctrl+N"), self, self.action_new)
        QShortcut(QKeySequence("Ctrl+O"), self, self.action_open)
        QShortcut(QKeySequence("Ctrl+S"), self, self.action_save)

        return bar

    def _open_file_in_text_editor(self, filepath):
        if os.name == 'nt':  # Windows
            os.startfile(filepath)
        elif os.name == 'posix':  # Linux/macOS
            subprocess.run(['xdg-open', filepath])
        
    def open_configure_editor(self):
        self._open_file_in_text_editor(CONFIG_PATH)

    def open_about(self):
        data={
            "version": about.__version__,
            "package": about.__package__,
            "program_name": about.__program_name__,
            "author": about.__author__,
            "email": about.__email__,
            "description": about.__description__,
            "url_source": about.__url_source__,
            "url_doc": about.__url_doc__,
            "url_funding": about.__url_funding__,
            "url_bugs": about.__url_bugs__
        }
        show_about_window(data,self.icon_path)

    def on_coffee_action_click(self):
        QDesktopServices.openUrl(QUrl("https://ko-fi.com/trucomanx"))

    def _build_header(self) -> QWidget:
        header = QWidget()
        header.setFixedHeight(80)
        header.setStyleSheet(f"background: {QColor(CONFIG['color_ui_header']).name()};")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(16, 8, 16, 8)

        # Breadcrumb + title area
        left = QVBoxLayout()
        left.setSpacing(2)

        self.breadcrumb_label = QLabel("⌂")
        self.breadcrumb_label.setStyleSheet("color: {CONFIG['color_ui_text']}; font-size: 11px;")
        left.addWidget(self.breadcrumb_label)

        self.title_label = QLabel(CONFIG["node_new_diagram_title"])
        self.title_label.setStyleSheet(f"color: {CONFIG['color_ui_text']}; font-size: 20px; font-weight: bold;")
        left.addWidget(self.title_label)

        self.summary_label = QLabel("")
        self.summary_label.setStyleSheet("color: {CONFIG['color_edge']}; font-size: 12px;")
        self.summary_label.setWordWrap(True)
        left.addWidget(self.summary_label)

        layout.addLayout(left, 1)

        # Edit button
        self.btn_edit_diagram = QPushButton(CONFIG["header_edit_button"])
        self.btn_edit_diagram.setFixedHeight(32)
        self.btn_edit_diagram.clicked.connect(self._edit_diagram_info)
        layout.addWidget(self.btn_edit_diagram)

        return header

    def _update_header(self):
        self.title_label.setText(self.current_diagram.title)
        summary_html = (self.current_diagram.summary or "").replace("\n", "<br>")
        self.summary_label.setText(summary_html)
        modified_indicator = " *" if self._modified else ""
        file_info = os.path.basename(self.current_filepath) if self.current_filepath else CONFIG["header_no_file"]
        self.setWindowTitle(f"{about.__program_name__} — {file_info}{modified_indicator}")

    def _update_breadcrumb(self):
        parts = self.nav_manager.get_breadcrumb(self.current_diagram.title)
        breadcrumb = " › ".join(parts)
        self.breadcrumb_label.setText(f"⌂  {breadcrumb}")

    def _update_back_button(self):
        self.btn_back.setEnabled(self.nav_manager.can_go_back())

    def _new_scene(self, diagram: Diagram):
        scene = DiagramScene(diagram, self)
        scene.diagram_changed.connect(self._on_diagram_changed)
        scene.show_grid = True
        self.view.setScene(scene)

    def _on_diagram_changed(self):
        self._modified = True
        self._update_header()

    def _edit_diagram_info(self):
        dlg = EditDiagramDialog(self.current_diagram.title, self.current_diagram.summary)
        if dlg.exec_() == QDialog.Accepted:
            self.current_diagram.title = dlg.title_edit.text().strip() or self.current_diagram.title
            self.current_diagram.summary = dlg.summary_edit.toPlainText().strip()
            self._update_header()
            self._update_breadcrumb()
            self._modified = True

    def _toggle_grid(self, checked: bool):
        if self.view.scene():
            self.view.scene().show_grid = checked
            self.view.scene().update()

    # ---- Actions ----

    def action_new(self):
        if self._modified:
            reply = QMessageBox.question(
                self, CONFIG["msg_title_save"],
                CONFIG["msg_save_before_new"],
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            if reply == QMessageBox.Yes:
                self.action_save()
            elif reply == QMessageBox.Cancel:
                return

        self.current_diagram = Diagram(CONFIG["node_new_diagram_title"], "")
        self.current_filepath = None
        self.nav_manager.clear()
        self._modified = False
        self._new_scene(self.current_diagram)
        self._update_header()
        self._update_breadcrumb()
        self._update_back_button()

    def action_open(self):
        if self._modified:
            reply = QMessageBox.question(
                self, CONFIG["msg_title_save"],
                CONFIG["msg_save_before_open"],
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            if reply == QMessageBox.Yes:
                self.action_save()
            elif reply == QMessageBox.Cancel:
                return

        filepath, _ = QFileDialog.getOpenFileName(
            self, CONFIG["file_dialog_open_title"], "", CONFIG["file_dialog_filter"])
        if filepath:
            self._load_file(filepath)

    def _load_file(self, filepath: str):
        try:
            diagram = DiagramSerializer.load(filepath)
            self.current_diagram = diagram
            self.current_filepath = filepath
            self._modified = False
            self.nav_manager.clear()
            self._new_scene(self.current_diagram)
            self._update_header()
            self._update_breadcrumb()
            self._update_back_button()
            self.statusBar().showMessage(CONFIG["statusbar_opened"].format(path=filepath))
        except Exception as ex:
            QMessageBox.critical(self, CONFIG["msg_title_error"], CONFIG["msg_error_open_file"].format(error=ex))

    def action_save(self):
        if not self.current_filepath:
            self.action_save_as()
        else:
            self._save_to(self.current_filepath)

    def action_save_as(self):
        filepath, _ = QFileDialog.getSaveFileName(
            self, CONFIG["file_dialog_save_title"], "", CONFIG["file_dialog_filter"])
        if filepath:
            if not filepath.endswith(".hdiagram"):
                filepath += ".hdiagram"
            self.current_filepath = filepath
            self._save_to(filepath)

    def _save_to(self, filepath: str):
        try:
            DiagramSerializer.save(self.current_diagram, filepath)
            self._modified = False
            self._update_header()
            self.statusBar().showMessage(CONFIG["statusbar_saved"].format(path=filepath))
        except Exception as ex:
            QMessageBox.critical(self, CONFIG["msg_title_error"], CONFIG["msg_error_save_file"].format(error=ex))

    def action_export_svg(self):
        filepath, _ = QFileDialog.getSaveFileName(
            self, CONFIG["file_dialog_export_svg_title"], "", CONFIG["file_dialog_filter_svg"])
        if not filepath:
            return
        if not filepath.endswith(".svg"):
            filepath += ".svg"
        try:
            scene = self.view.scene()
            if scene is None:
                return
            scene_rect = scene.itemsBoundingRect()
            margin = 20
            scene_rect.adjust(-margin, -margin, margin, margin)

            w = int(scene_rect.width())
            h = int(scene_rect.height())

            generator = QSvgGenerator()
            generator.setFileName(filepath)
            generator.setSize(scene_rect.size().toSize())
            generator.setViewBox(QRectF(0, 0, w, h))
            generator.setTitle(self.current_diagram.title)
            generator.setDescription(self.current_diagram.summary or "")

            painter = QPainter()
            painter.begin(generator)
            painter.setRenderHint(QPainter.Antialiasing)
            target_rect = QRectF(0, 0, w, h)
            scene.render(painter, target=target_rect, source=scene_rect)
            painter.end()

            self.statusBar().showMessage(CONFIG["statusbar_svg_exported"].format(path=filepath))
        except Exception as ex:
            QMessageBox.critical(self, CONFIG["msg_title_error"], CONFIG["msg_error_export_svg"].format(error=ex))

    def action_export_dot(self):
        filepath, _ = QFileDialog.getSaveFileName(
            self, CONFIG["file_dialog_export_dot_title"], "", CONFIG["file_dialog_filter_dot"])
        if not filepath:
            return
        if not filepath.endswith(".dot"):
            filepath += ".dot"
        try:
            dot = self._diagram_to_dot(self.current_diagram)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(dot)
            self.statusBar().showMessage(CONFIG["statusbar_dot_exported"].format(path=filepath))
        except Exception as ex:
            QMessageBox.critical(self, CONFIG["msg_title_error"], CONFIG["msg_error_export_dot"].format(error=ex))

    def _diagram_to_dot(self, diagram: Diagram) -> str:
        # Node type -> Graphviz shape mapping
        SHAPE = {
            Node.NODE_NORMAL: "box",
            Node.NODE_MERGE:  "diamond",
            Node.NODE_START:  "ellipse",
            Node.NODE_END:    "doublecircle",
        }
        COLOR = {
            Node.NODE_NORMAL: CONFIG["color_normal_border"],
            Node.NODE_MERGE:  CONFIG["color_merge_border"],
            Node.NODE_START:  CONFIG["color_start_border"],
            Node.NODE_END:    CONFIG["color_end_border"],
        }
        FONTCOLOR = {
            Node.NODE_NORMAL: CONFIG["color_normal_title"],
            Node.NODE_MERGE:  CONFIG["color_merge_title"],
            Node.NODE_START:  CONFIG["color_start_title"],
            Node.NODE_END:    CONFIG["color_end_title"],
        }
        FILLCOLOR = {
            Node.NODE_NORMAL: CONFIG["color_normal_bg"],
            Node.NODE_MERGE:  CONFIG["color_merge_bg"],
            Node.NODE_START:  CONFIG["color_start_bg"],
            Node.NODE_END:    CONFIG["color_end_bg"],
        }

        def esc(s: str) -> str:
            """Escape a string for use inside DOT double-quoted labels."""
            return s.replace("\\", "\\\\").replace('"', '\\"').replace('\n', '\\n')

        # Build a short stable id from the uuid (DOT node names can't have hyphens)
        def dot_id(node_id: str) -> str:
            return "n_" + node_id.replace("-", "_")

        lines = []
        graph_label = esc(diagram.title)
        if diagram.summary:
            graph_label += "\\n" + esc(diagram.summary)

        lines.append('digraph {')
        lines.append(f'    label="{graph_label}";')
        lines.append( '    labelloc="t";')
        lines.append( '    fontname="Helvetica";')
        lines.append( '    bgcolor="#1a1a2e";')
        lines.append( '    rankdir=LR;')
        lines.append( '    node [fontname="Helvetica" style="filled" penwidth=1.5];')
        lines.append( '    edge [color="#a0aec0" fontcolor="#a0aec0" fontname="Helvetica" fontsize=9];')
        lines.append('')

        # Nodes
        for node in diagram.nodes.values():
            nid    = dot_id(node.id)
            shape  = SHAPE.get(node.type, "box")
            color  = COLOR.get(node.type, "#ffffff")
            fc     = FONTCOLOR.get(node.type, "#ffffff")
            fill   = FILLCOLOR.get(node.type, "#2d3748")

            # Build label: title + optional summary + optional subdiagram indicator
            label = esc(node.title)
            if node.summary:
                label += "\\n" + esc(node.summary)
            if node.subdiagram:
                label += "\\n[» " + esc(node.subdiagram) + "]"

            # Position hint (Graphviz uses inches; divide pixels by 72)
            px = node.position[0] / 72.0
            py = node.position[1] / 72.0

            lines.append(
                f'    {nid} ['
                f'label="{label}" '
                f'shape="{shape}" '
                f'color="{color}" '
                f'fontcolor="{fc}" '
                f'fillcolor="{fill}" '
                f'pos="{px:.2f},{py:.2f}!" '
                f'];'
            )

        lines.append('')

        # Edges
        for edge in diagram.edges:
            src_node = diagram.nodes.get(edge.source_node_id)
            tgt_node = diagram.nodes.get(edge.target_node_id)
            if src_node is None or tgt_node is None:
                continue

            src_id = dot_id(edge.source_node_id)
            tgt_id = dot_id(edge.target_node_id)

            # Port names for the label
            src_port = ""
            tgt_port = ""
            if edge.source_output_index < len(src_node.outputs):
                src_port = src_node.outputs[edge.source_output_index]
            if edge.target_input_index < len(tgt_node.inputs):
                tgt_port = tgt_node.inputs[edge.target_input_index]

            edge_label = ""
            if src_port or tgt_port:
                edge_label = f'{esc(src_port)}→{esc(tgt_port)}'

            attr = f'label="{edge_label}" color="{CONFIG["color_edge"]}"'
            lines.append(f'    {src_id} -> {tgt_id} [{attr}];')

        lines.append('}')
        return '\n'.join(lines) + '\n'

    def action_back(self):
        if not self.nav_manager.can_go_back():
            return
        # Save current state first
        if self._modified and self.current_filepath:
            self._save_to(self.current_filepath)

        state = self.nav_manager.pop()
        if state:
            self.current_diagram = state["diagram"]
            self.current_filepath = state["filepath"]
            self._modified = False
            self._new_scene(self.current_diagram)
            self._update_header()
            self._update_breadcrumb()
            self._update_back_button()
            self.statusBar().showMessage(CONFIG["statusbar_returned"].format(title=self.current_diagram.title))

    def create_subdiagram_for_node(self, node_item: GraphicsNodeItem):
        node = node_item.node
        if node.type != Node.NODE_NORMAL:
            return

        # Ask for save location
        if not self.current_filepath:
            QMessageBox.warning(self, CONFIG["msg_title_warning"],
                                CONFIG["msg_save_before_subdiagram"])
            self.action_save()
            if not self.current_filepath:
                return

        base_dir = os.path.dirname(self.current_filepath)
        default_name = node.title.replace(" ", "_").lower() + ".hdiagram"
        filepath, _ = QFileDialog.getSaveFileName(
            self, CONFIG["file_dialog_save_sub_title"], os.path.join(base_dir, default_name),
            CONFIG["file_dialog_filter_hdiagram"]
        )
        if not filepath:
            return

        if not filepath.endswith(".hdiagram"):
            filepath += ".hdiagram"

        # Create new empty diagram
        new_diagram = Diagram(
            node.title + CONFIG["node_subdiagram_title_suffix"],
            CONFIG["node_subdiagram_summary_prefix"] + node.title + CONFIG["node_subdiagram_summary_suffix"]
        )
        # Add default start/end
        start = Node(Node.NODE_START, CONFIG["node_default_title_start"], "", 100, 200)
        end = Node(Node.NODE_END, CONFIG["node_default_title_end"], "", 500, 200)
        new_diagram.add_node(start)
        new_diagram.add_node(end)

        try:
            DiagramSerializer.save(new_diagram, filepath)
        except Exception as ex:
            QMessageBox.critical(self, CONFIG["msg_title_error"], CONFIG["msg_error_create_subdiagram"].format(error=ex))
            return

        # Set relative path
        rel_path = os.path.relpath(filepath, base_dir)
        node.subdiagram = rel_path
        node_item.update()
        self._modified = True
        self._update_header()

        # Navigate into subdiagram
        reply = QMessageBox.question(
            self, CONFIG["msg_title_navigate"],
            CONFIG["msg_subdiagram_created"].format(path=filepath),
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self._navigate_to(filepath, new_diagram)

    def open_subdiagram_for_node(self, node_item: GraphicsNodeItem):
        node = node_item.node
        if not node.subdiagram:
            return

        if not self.current_filepath:
            QMessageBox.warning(self, CONFIG["msg_title_warning"], CONFIG["msg_save_before_open_sub"])
            return

        base_dir = os.path.dirname(self.current_filepath)
        sub_path = os.path.join(base_dir, node.subdiagram)
        sub_path = os.path.normpath(sub_path)

        if not os.path.exists(sub_path):
            reply = QMessageBox.question(
                self, CONFIG["msg_title_file_not_found"],
                CONFIG["msg_subdiagram_not_found"].format(path=sub_path),
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.create_subdiagram_for_node(node_item)
            return

        try:
            sub_diagram = DiagramSerializer.load(sub_path)
            self._navigate_to(sub_path, sub_diagram)
        except Exception as ex:
            QMessageBox.critical(self, CONFIG["msg_title_error"], CONFIG["msg_error_open_subdiagram"].format(error=ex))

    def _navigate_to(self, filepath: str, diagram: Diagram):
        # Save current state to stack
        if self._modified and self.current_filepath:
            self._save_to(self.current_filepath)

        self.nav_manager.push(self.current_filepath, self.current_diagram)
        self.current_diagram = diagram
        self.current_filepath = filepath
        self._modified = False
        self._new_scene(self.current_diagram)
        self._update_header()
        self._update_breadcrumb()
        self._update_back_button()
        self.statusBar().showMessage(CONFIG["statusbar_navigating"].format(title=diagram.title))

    def closeEvent(self, event):
        if self._modified:
            reply = QMessageBox.question(
                self, CONFIG["msg_title_exit"],
                CONFIG["msg_save_before_exit"],
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            if reply == QMessageBox.Yes:
                self.action_save()
                event.accept()
            elif reply == QMessageBox.No:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


# ============================================================
# ENTRY POINT
# ============================================================

def main():

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    create_desktop_directory()    
    create_desktop_menu()
    create_desktop_file(os.path.join("~",".local","share","applications"), 
                        program_name=about.__program_name__)
    
    for n in range(len(sys.argv)):
        if sys.argv[n] == "--autostart":
            create_desktop_directory(overwrite = True)
            create_desktop_menu(overwrite = True)
            create_desktop_file(os.path.join("~",".config","autostart"), 
                                overwrite=True, 
                                program_name=about.__program_name__)
            return
        if sys.argv[n] == "--applications":
            create_desktop_directory(overwrite = True)
            create_desktop_menu(overwrite = True)
            create_desktop_file(os.path.join("~",".local","share","applications"), 
                                overwrite=True, 
                                program_name=about.__program_name__)
            return
    
    app = QApplication(sys.argv)
    app.setApplicationName(about.__package__) 

    app.setStyle("Fusion")
    
    # Dark palette base
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(CONFIG["color_ui_background"]))
    palette.setColor(QPalette.WindowText, QColor(CONFIG["color_ui_text"]))
    palette.setColor(QPalette.Base, QColor(CONFIG["color_ui_base"]))
    palette.setColor(QPalette.AlternateBase, QColor(CONFIG["color_ui_header"]))
    palette.setColor(QPalette.ToolTipBase, QColor(CONFIG["color_ui_base"]))
    palette.setColor(QPalette.ToolTipText, QColor(CONFIG["color_ui_text"]))
    palette.setColor(QPalette.Text, QColor(CONFIG["color_ui_text"]))
    palette.setColor(QPalette.Button, QColor(CONFIG["color_ui_base"]))
    palette.setColor(QPalette.ButtonText, QColor(CONFIG["color_ui_text"]))
    palette.setColor(QPalette.Highlight, QColor(CONFIG["color_ui_border"]))
    palette.setColor(QPalette.HighlightedText, QColor(CONFIG["color_ui_highlighted_text"]))
    app.setPalette(palette)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
