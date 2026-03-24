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
    "toolbar_configure": "Configure",
    "toolbar_configure_tooltip": "Open the configure Json file of program GUI",
    "toolbar_about": "About",
    "toolbar_about_tooltip": "About the program",
    "toolbar_coffee": "Coffee",
    "toolbar_coffee_tooltip": "Buy me a coffee (TrucomanX)",
    "window_width": 1024,
    "window_height": 800,
    "port_radius": 6,
    "port_hit_radius": 10,
    "node_min_width": 140,
    "node_min_height": 70,
    "grid_size": 20,
    "edge_hit_tolerance": 8,
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
    "color_text": "#e2e8f0",
    "color_subdiagram": "#9f7aea",
    "color_grid": "#2a2a3e",
    "color_background": "#1a1a2e",
    "color_breadcrumb_bg": "#2d3748",
    "color_header_bg": "#1e2433",
    "color_selection": [100, 149, 237, 80],
    "palette_window": "#1a1a2e",
    "palette_window_text": "#e2e8f0",
    "palette_base": "#2d3748",
    "palette_alternate_base": "#1e2433",
    "palette_tooltip_base": "#2d3748",
    "palette_tooltip_text": "#e2e8f0",
    "palette_text": "#e2e8f0",
    "palette_button": "#2d3748",
    "palette_button_text": "#e2e8f0",
    "palette_highlight": "#4a90d9",
    "palette_highlighted_text": "#ffffff"
}

configure.verify_default_config(CONFIG_PATH,default_content=DEFAULT_CONTENT)

CONFIG=configure.load_config(CONFIG_PATH)

# ============================================================
# CONSTANTS
# ============================================================

PORT_RADIUS = CONFIG["port_radius"]
PORT_HIT_RADIUS = CONFIG["port_hit_radius"]
NODE_MIN_WIDTH = CONFIG["node_min_width"]
NODE_MIN_HEIGHT = CONFIG["node_min_height"]
GRID_SIZE = CONFIG["grid_size"]
EDGE_HIT_TOLERANCE = CONFIG["edge_hit_tolerance"]

COLORS = {
    "normal_bg": QColor("#2d3748"),
    "normal_border": QColor("#4a90d9"),
    "normal_title": QColor("#63b3ed"),
    "merge_bg": QColor("#2d4a3e"),
    "merge_border": QColor("#48bb78"),
    "merge_title": QColor("#68d391"),
    "start_bg": QColor("#2d3a1e"),
    "start_border": QColor("#9ae600"),
    "start_title": QColor("#b5f542"),
    "end_bg": QColor("#4a1e1e"),
    "end_border": QColor("#fc8181"),
    "end_title": QColor("#feb2b2"),
    "port_input": QColor("#63b3ed"),
    "port_output": QColor("#f6ad55"),
    "port_hover": QColor("#ffffff"),
    "edge": QColor("#a0aec0"),
    "edge_selected": QColor("#ffd700"),
    "edge_point": QColor("#ffd700"),
    "text": QColor("#e2e8f0"),
    "subdiagram": QColor("#9f7aea"),
    "grid": QColor("#2a2a3e"),
    "background": QColor("#1a1a2e"),
    "breadcrumb_bg": QColor("#2d3748"),
    "header_bg": QColor(CONFIG["color_header_bg"]),
    "selection": QColor(*CONFIG["color_selection"]),
}

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
    Returns dict with port positions relative to node center (0,0).
    Accounts for rotation.
    """
    rot = node.rotation % 360
    # Base: inputs on left, outputs on right
    # After rotation, positions transform accordingly

    n_in = len(node.inputs)
    n_out = len(node.outputs)

    hw = rect_width / 2
    hh = rect_height / 2

    # After 90/270 rotation the visual width and height swap
    if rot in (90, 270):
        vis_hw, vis_hh = hh, hw
    else:
        vis_hw, vis_hh = hw, hh

    # For merge nodes, ports attach to the narrow bar edges.
    # bar_w tracks 38% of the visual width so it always matches the narrow side.
    is_merge = node.type == "merge"
    if is_merge:
        bar_w = max(vis_hw * 0.38, 18)
        port_x_in  = -bar_w
        port_x_out =  bar_w
    else:
        port_x_in  = -hw
        port_x_out =  hw

    input_positions = []
    for i in range(n_in):
        if n_in == 1:
            t = 0.5
        else:
            t = (i + 1) / (n_in + 1)
        # left side
        px = port_x_in
        py = -hh + t * rect_height
        input_positions.append(QPointF(px, py))

    output_positions = []
    for i in range(n_out):
        if n_out == 1:
            t = 0.5
        else:
            t = (i + 1) / (n_out + 1)
        # right side
        px = port_x_out
        py = -hh + t * rect_height
        output_positions.append(QPointF(px, py))

    # Apply rotation transform
    transform = QTransform()
    transform.rotate(rot)

    rotated_inputs = [transform.map(p) for p in input_positions]
    rotated_outputs = [transform.map(p) for p in output_positions]

    return rotated_inputs, rotated_outputs


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
            color = COLORS["port_hover"]
        elif self.is_input:
            color = COLORS["port_input"]
        else:
            color = COLORS["port_output"]
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

        # Merge nodes get a narrower, taller default footprint
        if node.type == Node.NODE_MERGE:
            self.width = NODE_MIN_WIDTH
            self.height = NODE_MIN_HEIGHT * 2  # tall bar
        else:
            self.width = NODE_MIN_WIDTH
            self.height = NODE_MIN_HEIGHT
        self._hovered = False
        self._port_items: List[GraphicsPortItem] = []

        self.setPos(node.position[0], node.position[1])
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
        # Account for rotation
        rot = self.node.rotation % 360
        if rot in (90, 270):
            hw, hh = hh, hw
        return QRectF(-hw - PORT_RADIUS - 2, -hh - PORT_RADIUS - 2,
                      hw * 2 + (PORT_RADIUS + 2) * 2,
                      hh * 2 + (PORT_RADIUS + 2) * 2)

    def _get_shape_path(self) -> QPainterPath:
        rot = self.node.rotation % 360
        if rot in (90, 270):
            hw, hh = self.height / 2, self.width / 2
        else:
            hw, hh = self.width / 2, self.height / 2

        path = QPainterPath()
        if self.node.type == Node.NODE_START:
            # Rounded left, flat right - arrow pointing right
            rect = QRectF(-hw, -hh, hw * 2, hh * 2)
            path.addRoundedRect(rect, hh * 0.8, hh * 0.8)
        elif self.node.type == Node.NODE_END:
            # Flat left, pointed right - target shape
            rect = QRectF(-hw, -hh, hw * 2, hh * 2)
            path.addRoundedRect(rect, 8, 8)
        elif self.node.type == Node.NODE_MERGE:
            # Vertical bar — narrow width, tall height, slightly rounded corners
            bar_w = max(hw * 0.38, 18)
            bar_h = hh
            rect = QRectF(-bar_w, -bar_h, bar_w * 2, bar_h * 2)
            path.addRoundedRect(rect, 6, 6)
        else:
            rect = QRectF(-hw, -hh, hw * 2, hh * 2)
            path.addRoundedRect(rect, 10, 10)
        return path

    def paint(self, painter: QPainter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing)

        rot = self.node.rotation % 360
        if rot in (90, 270):
            hw, hh = self.height / 2, self.width / 2
        else:
            hw, hh = self.width / 2, self.height / 2

        # Colors based on type
        t = self.node.type
        if t == Node.NODE_NORMAL:
            bg = COLORS["normal_bg"]
            border = COLORS["normal_border"]
            title_color = COLORS["normal_title"]
        elif t == Node.NODE_MERGE:
            bg = COLORS["merge_bg"]
            border = COLORS["merge_border"]
            title_color = COLORS["merge_title"]
        elif t == Node.NODE_START:
            bg = COLORS["start_bg"]
            border = COLORS["start_border"]
            title_color = COLORS["start_title"]
        else:  # END
            bg = COLORS["end_bg"]
            border = COLORS["end_border"]
            title_color = COLORS["end_title"]

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
        pen_color = border if not self.isSelected() else COLORS["edge_selected"]
        pen_width = 2.5 if self.isSelected() else 1.5
        painter.setPen(QPen(pen_color, pen_width))
        painter.drawPath(path)

        # Sub-indicator line (if has subdiagram)
        if self.node.subdiagram and t == Node.NODE_NORMAL:
            painter.setPen(QPen(COLORS["subdiagram"], 1.5, Qt.DashLine))
            painter.setBrush(Qt.NoBrush)
            rect_inner = QRectF(-hw + 4, -hh + 4, hw * 2 - 8, hh * 2 - 8)
            painter.drawRoundedRect(rect_inner, 7, 7)

        # Title text
        painter.setPen(QPen(title_color))
        font = QFont("Segoe UI", 9, QFont.Bold)
        painter.setFont(font)
        title_rect = QRectF(-hw + 8, -hh + 5, hw * 2 - 16, hh - 5)
        painter.drawText(title_rect, Qt.AlignHCenter | Qt.AlignTop | Qt.TextWordWrap,
                         self.node.title)

        # Summary text (only for normal)
        if self.node.type == Node.NODE_NORMAL and self.node.summary:
            painter.setPen(QPen(COLORS["text"].darker(110)))
            font2 = QFont("Segoe UI", 7)
            painter.setFont(font2)
            summary_rect = QRectF(-hw + 8, 2, hw * 2 - 16, hh - 8)
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
        font3 = QFont("Segoe UI", 7)
        painter.setFont(font3)
        badge_rect = QRectF(hw - 26, hh - 16, 22, 12)
        painter.drawText(badge_rect, Qt.AlignRight | Qt.AlignBottom, type_text)

        # Port labels
        input_pos, output_pos = get_port_positions(self.node, self.width, self.height)
        font4 = QFont("Segoe UI", 6)
        painter.setFont(font4)
        for i, pos in enumerate(input_pos):
            if i < len(self.node.inputs):
                lbl = self.node.inputs[i]
                painter.setPen(QPen(COLORS["port_input"].lighter(130)))
                lr = QRectF(pos.x() + PORT_RADIUS + 2, pos.y() - 8, 40, 16)
                painter.drawText(lr, Qt.AlignLeft | Qt.AlignVCenter, lbl)
        for i, pos in enumerate(output_pos):
            if i < len(self.node.outputs):
                lbl = self.node.outputs[i]
                painter.setPen(QPen(COLORS["port_output"].lighter(130)))
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
            act_edit = menu.addAction(QIcon.fromTheme("document-edit"), "Editar título/resumo")
            act_edit.triggered.connect(self._edit_title_summary)

        if t == Node.NODE_NORMAL:
            menu.addSeparator()
            act_ai = menu.addAction(QIcon.fromTheme("list-add"), "Adicionar entrada")
            act_ai.triggered.connect(self._add_input)
            act_ri = menu.addAction(QIcon.fromTheme("list-remove"), "Remover última entrada")
            act_ri.triggered.connect(self._remove_input)
            act_ao = menu.addAction(QIcon.fromTheme("list-add"), "Adicionar saída")
            act_ao.triggered.connect(self._add_output)
            act_ro = menu.addAction(QIcon.fromTheme("list-remove"), "Remover última saída")
            act_ro.triggered.connect(self._remove_output)
            menu.addSeparator()
            if self.node.subdiagram:
                act_open = menu.addAction(QIcon.fromTheme("document-open"), "Abrir subdiagrama")
                act_open.triggered.connect(self._open_subdiagram)
            else:
                act_create = menu.addAction(QIcon.fromTheme("document-new"), "Criar subdiagrama")
                act_create.triggered.connect(self._create_subdiagram)

        if t == Node.NODE_MERGE:
            menu.addSeparator()
            act_ai = menu.addAction(QIcon.fromTheme("list-add"), "Adicionar entrada")
            act_ai.triggered.connect(self._add_input)
            act_ri = menu.addAction(QIcon.fromTheme("list-remove"), "Remover última entrada")
            act_ri.triggered.connect(self._remove_input)

        menu.addSeparator()
        act_rot = menu.addAction(QIcon.fromTheme("object-rotate-right"), "Rotacionar 90°")
        act_rot.triggered.connect(self._rotate)
        menu.addSeparator()
        act_del = menu.addAction(QIcon.fromTheme("edit-delete"), "Deletar")
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
            color = COLORS["edge_selected"]
            width = 2.5
        else:
            color = COLORS["edge"]
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
            painter.setBrush(QBrush(COLORS["edge_point"]))
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
        color = COLORS["edge_selected"] if (self.isSelected() or self._hovered) else COLORS["edge"]
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
        act_del = menu.addAction(QIcon.fromTheme("edit-delete"), "Deletar conexão")
        act_del.triggered.connect(self._delete)
        act_clr = menu.addAction(QIcon.fromTheme("edit-clear"), "Limpar pontos intermediários")
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
        pen = QPen(COLORS["port_output"], 2, Qt.DashLine)
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
        self.setBackgroundBrush(QBrush(COLORS["background"]))

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
            Node.NODE_NORMAL: "Função",
            Node.NODE_MERGE: "Merge",
            Node.NODE_START: "Início",
            Node.NODE_END: "Fim"
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
            act_normal = menu.addAction(QIcon.fromTheme("list-add"), "Adicionar Bloco Normal")
            act_merge = menu.addAction(QIcon.fromTheme("list-add"), "Adicionar Bloco Merge")
            act_start = menu.addAction(QIcon.fromTheme("media-playback-start"), "Bloco Start")
            act_end = menu.addAction(QIcon.fromTheme("media-playback-stop"), "Bloco End")

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
            painter.setPen(QPen(COLORS["grid"], 0.5))
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
        self.setWindowTitle("Editar Bloco")
        self.setMinimumWidth(400)
        self.setMinimumHeight(250)

        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        main_layout.addLayout(form_layout)

        self.title_edit = QLineEdit(title)
        form_layout.addRow("Título:", self.title_edit)

        self.summary_edit = QTextEdit()
        self.summary_edit.setPlainText(summary)
        self.summary_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        if show_summary:
            form_layout.addRow("Resumo:", self.summary_edit)
            main_layout.setStretchFactor(form_layout, 1)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)

        self.setStyleSheet("""
            QDialog { background: #2d3748; color: #e2e8f0; }
            QLineEdit, QTextEdit { background: #1a1a2e; color: #e2e8f0;
                                   border: 1px solid #4a90d9; border-radius: 4px;
                                   padding: 4px; }
            QLabel { color: #a0aec0; }
            QPushButton { background: #4a90d9; color: white; border-radius: 4px;
                          padding: 6px 16px; border: none; }
            QPushButton:hover { background: #63b3ed; }
        """)


class EditDiagramDialog(QDialog):
    def __init__(self, title: str, summary: str):
        super().__init__()
        self.setWindowTitle("Editar Diagrama")
        self.setMinimumWidth(450)
        self.setMinimumHeight(280)

        main_layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        main_layout.addLayout(form_layout)

        self.title_edit = QLineEdit(title)
        form_layout.addRow("Título:", self.title_edit)

        self.summary_edit = QTextEdit()
        self.summary_edit.setPlainText(summary)
        self.summary_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        form_layout.addRow("Resumo:", self.summary_edit)
        main_layout.setStretchFactor(form_layout, 1)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)

        self.setStyleSheet("""
            QDialog { background: #2d3748; color: #e2e8f0; }
            QLineEdit, QTextEdit { background: #1a1a2e; color: #e2e8f0;
                                   border: 1px solid #4a90d9; border-radius: 4px;
                                   padding: 4px; }
            QLabel { color: #a0aec0; }
            QPushButton { background: #4a90d9; color: white; border-radius: 4px;
                          padding: 6px 16px; border: none; }
            QPushButton:hover { background: #63b3ed; }
        """)


# ============================================================
# MAIN WINDOW
# ============================================================

STYLE_SHEET = """
QMainWindow { background: #1a1a2e; }
QWidget { background: #1a1a2e; color: #e2e8f0; font-family: 'Segoe UI', Arial, sans-serif; }

QPushButton {
    background: #2d3748;
    color: #a0aec0;
    border: 1px solid #4a5568;
    border-radius: 5px;
    padding: 5px 12px;
    font-size: 12px;
}
QPushButton:hover {
    background: #4a5568;
    color: #e2e8f0;
}
QPushButton:pressed {
    background: #4a90d9;
    color: white;
}
QPushButton:disabled {
    color: #4a5568;
    border-color: #2d3748;
}

QToolBar {
    background: #1e2433;
    border-bottom: 1px solid #2d3748;
    spacing: 4px;
    padding: 4px;
}

QLabel { background: transparent; }

QScrollBar:vertical {
    background: #1a1a2e;
    width: 8px;
}
QScrollBar::handle:vertical {
    background: #4a5568;
    border-radius: 4px;
}
QScrollBar:horizontal {
    background: #1a1a2e;
    height: 8px;
}
QScrollBar::handle:horizontal {
    background: #4a5568;
    border-radius: 4px;
}

QMenu {
    background: #2d3748;
    border: 1px solid #4a5568;
    color: #e2e8f0;
    padding: 4px;
}
QMenu::item:selected {
    background: #4a90d9;
    border-radius: 3px;
}
QMenu::separator {
    height: 1px;
    background: #4a5568;
    margin: 3px 0;
}
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
        self.current_diagram: Diagram = Diagram("New Diagram", "")
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
        divider.setStyleSheet("background: #2d3748;")
        main_layout.addWidget(divider)

        # Graphics view
        self.view = DiagramView()
        self.view.setMinimumHeight(400)
        main_layout.addWidget(self.view, 1)

        # Status bar
        self.statusBar().setStyleSheet("background: #1e2433; color: #718096; font-size: 11px;")
        self.statusBar().showMessage("Pronto | Clique direito na área para adicionar blocos | "
                                     "Arraste portas para conectar | F = Ajustar | Scroll = Zoom")

    def _build_toolbar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(44)
        bar.setStyleSheet("background: #1e2433; border-bottom: 1px solid #2d3748;")
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

        self.btn_new     = btn("document-new",      "Novo",       "Novo diagrama (Ctrl+N)",          self.action_new)
        self.btn_open    = btn("document-open",     "Abrir",      "Abrir arquivo .hdiagram (Ctrl+O)", self.action_open)
        self.btn_save    = btn("document-save",     "Salvar",     "Salvar (Ctrl+S)",                 self.action_save)
        self.btn_save_as = btn("document-save-as",  "Salvar Como","Salvar como...",                  self.action_save_as)

        layout.addWidget(self.btn_new)
        layout.addWidget(self.btn_open)
        layout.addWidget(self.btn_save)
        layout.addWidget(self.btn_save_as)

        # Separator
        sep = QWidget()
        sep.setFixedWidth(1)
        sep.setFixedHeight(24)
        sep.setStyleSheet("background: #4a5568;")
        layout.addWidget(sep)

        self.btn_back = btn("go-previous", "Voltar", "Voltar ao diagrama anterior", self.action_back)
        self.btn_back.setEnabled(False)
        layout.addWidget(self.btn_back)

        layout.addStretch()

        # Grid toggle
        self.btn_grid = QPushButton("Grid")
        grid_icon = QIcon.fromTheme("view-grid")
        if not grid_icon.isNull():
            self.btn_grid.setIcon(grid_icon)
        self.btn_grid.setCheckable(True)
        self.btn_grid.setChecked(True)
        self.btn_grid.setFixedHeight(32)
        self.btn_grid.clicked.connect(self._toggle_grid)
        layout.addWidget(self.btn_grid)

        # Fit view
        btn_fit = QPushButton("Ajustar")
        fit_icon = QIcon.fromTheme("zoom-fit-best")
        if not fit_icon.isNull():
            btn_fit.setIcon(fit_icon)
        btn_fit.setFixedHeight(32)
        btn_fit.clicked.connect(lambda: self.view.fit_in_view())
        layout.addWidget(btn_fit)

        # Configure
        btn_configure = QPushButton("Configure")
        configure_icon = QIcon.fromTheme("document-properties")
        if not configure_icon.isNull():
            btn_configure.setIcon(configure_icon)
        btn_configure.setFixedHeight(32)
        btn_configure.clicked.connect(lambda: self.open_configure_editor())
        layout.addWidget(btn_configure)

        # Coffee
        btn_coffee = QPushButton("Coffee")
        coffee_icon = QIcon.fromTheme("emblem-favorite")
        if not coffee_icon.isNull():
            btn_coffee.setIcon(coffee_icon)
        btn_coffee.setFixedHeight(32)
        btn_coffee.clicked.connect(lambda: self.on_coffee_action_click())
        layout.addWidget(btn_coffee)

        # About
        btn_about = QPushButton("About")
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
        header.setStyleSheet(f"background: {COLORS['header_bg'].name()};")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(16, 8, 16, 8)

        # Breadcrumb + title area
        left = QVBoxLayout()
        left.setSpacing(2)

        self.breadcrumb_label = QLabel("⌂")
        self.breadcrumb_label.setStyleSheet("color: #718096; font-size: 11px;")
        left.addWidget(self.breadcrumb_label)

        self.title_label = QLabel("New Diagram")
        self.title_label.setStyleSheet("color: #e2e8f0; font-size: 20px; font-weight: bold;")
        left.addWidget(self.title_label)

        self.summary_label = QLabel("")
        self.summary_label.setStyleSheet("color: #a0aec0; font-size: 12px;")
        self.summary_label.setWordWrap(True)
        left.addWidget(self.summary_label)

        layout.addLayout(left, 1)

        # Edit button
        self.btn_edit_diagram = QPushButton("✏ Editar Info")
        self.btn_edit_diagram.setFixedHeight(32)
        self.btn_edit_diagram.clicked.connect(self._edit_diagram_info)
        layout.addWidget(self.btn_edit_diagram)

        return header

    def _update_header(self):
        self.title_label.setText(self.current_diagram.title)
        summary_html = (self.current_diagram.summary or "").replace("\n", "<br>")
        self.summary_label.setText(summary_html)
        modified_indicator = " *" if self._modified else ""
        file_info = os.path.basename(self.current_filepath) if self.current_filepath else "Sem arquivo"
        self.setWindowTitle(f"Hierarchical Diagram Editor — {file_info}{modified_indicator}")

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
                self, "Salvar?",
                "Diagrama modificado. Deseja salvar antes de criar novo?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            if reply == QMessageBox.Yes:
                self.action_save()
            elif reply == QMessageBox.Cancel:
                return

        self.current_diagram = Diagram("New Diagram", "")
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
                self, "Salvar?",
                "Diagrama modificado. Deseja salvar antes de abrir?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            if reply == QMessageBox.Yes:
                self.action_save()
            elif reply == QMessageBox.Cancel:
                return

        filepath, _ = QFileDialog.getOpenFileName(
            self, "Abrir Diagrama", "", "Hierarchical Diagram Files (*.hdiagram);;All Files (*)")
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
            self.statusBar().showMessage(f"Aberto: {filepath}")
        except Exception as ex:
            QMessageBox.critical(self, "Erro", f"Não foi possível abrir o arquivo:\n{ex}")

    def action_save(self):
        if not self.current_filepath:
            self.action_save_as()
        else:
            self._save_to(self.current_filepath)

    def action_save_as(self):
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Salvar Diagrama Como", "", "Hierarchical Diagram Files (*.hdiagram);;All Files (*)")
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
            self.statusBar().showMessage(f"Salvo: {filepath}")
        except Exception as ex:
            QMessageBox.critical(self, "Erro", f"Não foi possível salvar:\n{ex}")

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
            self.statusBar().showMessage(f"Voltou para: {self.current_diagram.title}")

    def create_subdiagram_for_node(self, node_item: GraphicsNodeItem):
        node = node_item.node
        if node.type != Node.NODE_NORMAL:
            return

        # Ask for save location
        if not self.current_filepath:
            QMessageBox.warning(self, "Aviso",
                                "Salve o diagrama atual primeiro antes de criar subdiagrama.")
            self.action_save()
            if not self.current_filepath:
                return

        base_dir = os.path.dirname(self.current_filepath)
        default_name = node.title.replace(" ", "_").lower() + ".hdiagram"
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Create Subdiagram", os.path.join(base_dir, default_name),
            "Hierarchical Diagram Files (*.hdiagram)"
        )
        if not filepath:
            return

        if not filepath.endswith(".hdiagram"):
            filepath += ".hdiagram"

        # Create new empty diagram
        new_diagram = Diagram(node.title + " -- Subdiagram", f"Subdiagram of '{node.title}'")
        # Add default start/end
        start = Node(Node.NODE_START, "Start", "", 100, 200)
        end = Node(Node.NODE_END, "End", "", 500, 200)
        new_diagram.add_node(start)
        new_diagram.add_node(end)

        try:
            DiagramSerializer.save(new_diagram, filepath)
        except Exception as ex:
            QMessageBox.critical(self, "Error", f"Unable to create subdiagram:\n{ex}")
            return

        # Set relative path
        rel_path = os.path.relpath(filepath, base_dir)
        node.subdiagram = rel_path
        node_item.update()
        self._modified = True
        self._update_header()

        # Navigate into subdiagram
        reply = QMessageBox.question(
            self, "Navigate",
            f"Subdiagram created in '{filepath}'.\nDo you want to navigate to it?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self._navigate_to(filepath, new_diagram)

    def open_subdiagram_for_node(self, node_item: GraphicsNodeItem):
        node = node_item.node
        if not node.subdiagram:
            return

        if not self.current_filepath:
            QMessageBox.warning(self, "Warning", "Save the current diagram first.")
            return

        base_dir = os.path.dirname(self.current_filepath)
        sub_path = os.path.join(base_dir, node.subdiagram)
        sub_path = os.path.normpath(sub_path)

        if not os.path.exists(sub_path):
            reply = QMessageBox.question(
                self, "File not found",
                f"The file '{sub_path}' does not exist.\nDo you want to create a new subdiagram?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.create_subdiagram_for_node(node_item)
            return

        try:
            sub_diagram = DiagramSerializer.load(sub_path)
            self._navigate_to(sub_path, sub_diagram)
        except Exception as ex:
            QMessageBox.critical(self, "Error", f"Unable to open subdiagram:\n{ex}")

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
        self.statusBar().showMessage(f"Navigating to: {diagram.title}")

    def closeEvent(self, event):
        if self._modified:
            reply = QMessageBox.question(
                self, "Exit",
                "Diagram modified. Do you want to save before exiting?",
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
    
    '''
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
    '''
    
    app = QApplication(sys.argv)
    app.setApplicationName(about.__package__) 

    app.setStyle("Fusion")
    
    # Dark palette base
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(CONFIG["palette_window"]))
    palette.setColor(QPalette.WindowText, QColor(CONFIG["palette_window_text"]))
    palette.setColor(QPalette.Base, QColor(CONFIG["palette_base"]))
    palette.setColor(QPalette.AlternateBase, QColor(CONFIG["palette_alternate_base"]))
    palette.setColor(QPalette.ToolTipBase, QColor(CONFIG["palette_tooltip_base"]))
    palette.setColor(QPalette.ToolTipText, QColor(CONFIG["palette_tooltip_text"]))
    palette.setColor(QPalette.Text, QColor(CONFIG["palette_text"]))
    palette.setColor(QPalette.Button, QColor(CONFIG["palette_button"]))
    palette.setColor(QPalette.ButtonText, QColor(CONFIG["palette_button_text"]))
    palette.setColor(QPalette.Highlight, QColor(CONFIG["palette_highlight"]))
    palette.setColor(QPalette.HighlightedText, QColor(CONFIG["palette_highlighted_text"]))
    app.setPalette(palette)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
