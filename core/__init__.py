"""
Core модули для Simple Time Tracker
Поддержка иерархических проектов и отслеживания активности
"""

from .transliteration import transliterate, generate_id_from_title, generate_path_from_title
from .compatibility import detect_db_format, ensure_project_fields, get_aggregated_minutes_compat
from .hierarchy import (
    calculate_aggregated_minutes, 
    update_aggregated_minutes,
    get_all_parent_paths,
    is_direct_child,
    find_project_by_path,
    get_project_level
)
from .active import UserActivityMonitor, create_activity_monitor_from_config

__all__ = [
    'transliterate',
    'generate_id_from_title', 
    'generate_path_from_title',
    'detect_db_format',
    'ensure_project_fields',
    'get_aggregated_minutes_compat',
    'calculate_aggregated_minutes',
    'update_aggregated_minutes',
    'get_all_parent_paths',
    'is_direct_child',
    'find_project_by_path',
    'get_project_level',
    'UserActivityMonitor',
    'create_activity_monitor_from_config'
]
