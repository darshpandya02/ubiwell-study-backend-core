# study_framework_core/core/navigation_registry.py

class NavigationRegistry:
    """
    Centralized registry for navigation items.
    Allows extensions to register their own navigation items.
    """
    
    def __init__(self):
        self._items = []
        self._user_menu_items = []
        
    def register_item(self, item, position=None):
        """
        Register a navigation item.
        
        Args:
            item (dict): Navigation item with keys:
                - label (str): Display text
                - icon (str): FontAwesome icon class
                - url (str): URL path or endpoint name
                - url_for (bool): If True, use url_for() with the url value
                - position (int): Optional position override
                - permission (str): Optional permission required
            position (int): Where to insert the item (None = append to end)
        """
        if position is not None:
            item['position'] = position
        else:
            item['position'] = item.get('position', 999)
            
        self._items.append(item)
        # Sort by position
        self._items.sort(key=lambda x: x['position'])
        
    def register_user_menu_item(self, item, position=None):
        """
        Register an item for the user dropdown menu (right side of navbar).
        
        Args:
            item (dict): User menu item with same structure as register_item
            position (int): Where to insert the item
        """
        if position is not None:
            item['position'] = position
        else:
            item['position'] = item.get('position', 999)
            
        self._user_menu_items.append(item)
        self._user_menu_items.sort(key=lambda x: x['position'])
    
    def get_items(self, user_permissions=None):
        """
        Get all registered navigation items.
        
        Args:
            user_permissions (list): List of user permissions to filter items
            
        Returns:
            list: Filtered navigation items
        """
        if user_permissions is None:
            return [item for item in self._items]
        
        return [
            item for item in self._items 
            if not item.get('permission') or item.get('permission') in user_permissions
        ]
    
    def get_user_menu_items(self, user_permissions=None):
        """Get user menu items (for dropdown)."""
        if user_permissions is None:
            return [item for item in self._user_menu_items]
        
        return [
            item for item in self._user_menu_items 
            if not item.get('permission') or item.get('permission') in user_permissions
        ]
    
    def clear(self):
        """Clear all registered items (useful for testing)."""
        self._items = []
        self._user_menu_items = []


# Global registry instance
_nav_registry = NavigationRegistry()


def get_navigation_registry():
    """Get the global navigation registry instance."""
    return _nav_registry


def register_core_navigation():
    """Register default/core navigation items."""
    registry = get_navigation_registry()
    
    # Core navigation items - using direct URLs instead of endpoint names
    # to avoid Flask-RESTful endpoint name issues
    registry.register_item({
        'label': 'Dashboard',
        'icon': 'fas fa-home',
        'url': '/internal_web/dashboard',
        'url_for': False,
        'position': 10
    })
    
    registry.register_item({
        'label': 'User Management',
        'icon': 'fas fa-users',
        'url': '/internal_web/user-management',
        'url_for': False,
        'position': 20
    })
    
    registry.register_item({
        'label': 'EMA Schedule',
        'icon': 'fas fa-calendar-alt',
        'url': '/internal_web/ema-schedule',
        'url_for': False,
        'position': 30
    })
    
    registry.register_item({
        'label': 'Config Management',
        'icon': 'fas fa-cogs',
        'url': '/internal_web/config-schedule',
        'url_for': False,
        'position': 40
    })
    
    registry.register_item({
        'label': 'Data Export',
        'icon': 'fas fa-download',
        'url': '/internal_web/download_compliance',
        'url_for': False,
        'position': 50
    })