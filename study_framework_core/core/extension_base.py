# study_framework_core/core/extension_base.py

from abc import ABC, abstractmethod
from .navigation_registry import get_navigation_registry


class DashboardExtension(ABC):
    """
    Base class for dashboard extensions.
    Extensions should inherit from this class and implement the required methods.
    """
    
    def __init__(self, app, config):
        """
        Initialize the extension.
        
        Args:
            app: Flask application instance
            config: Configuration dictionary
        """
        self.app = app
        self.config = config
        self.nav_registry = get_navigation_registry()
    
    @abstractmethod
    def get_name(self):
        """Return the name of the extension."""
        pass
    
    @abstractmethod
    def get_version(self):
        """Return the version of the extension."""
        pass
    
    def register_navigation(self):
        """
        Register navigation items for this extension.
        Override this method to add custom navigation items.
        """
        pass
    
    def register_routes(self):
        """
        Register Flask routes for this extension.
        Override this method to add custom routes.
        """
        pass
    
    def register_templates(self):
        """
        Register template folders for this extension.
        Override this method to add custom template directories.
        
        Returns:
            str or list: Path(s) to template directory/directories
        """
        return None
    
    def register_static(self):
        """
        Register static folders for this extension.
        Override this method to add custom static directories.
        
        Returns:
            str or list: Path(s) to static directory/directories
        """
        return None
    
    def initialize(self):
        """
        Initialize the extension.
        Called after all registrations are complete.
        Override this method for any initialization logic.
        """
        pass


class ExtensionManager:
    """Manages loading and initialization of dashboard extensions."""
    
    def __init__(self, app, config):
        self.app = app
        self.config = config
        self.extensions = []
    
    def register_extension(self, extension_class):
        """
        Register and initialize an extension.
        
        Args:
            extension_class: Class that inherits from DashboardExtension
        """
        extension = extension_class(self.app, self.config)
        
        # Register templates
        template_dirs = extension.register_templates()
        if template_dirs:
            if isinstance(template_dirs, str):
                template_dirs = [template_dirs]
            for template_dir in template_dirs:
                self.app.jinja_loader.searchpath.append(template_dir)
        
        # Register navigation
        extension.register_navigation()
        
        # Register routes
        extension.register_routes()
        
        # Initialize
        extension.initialize()
        
        self.extensions.append(extension)
        
        return extension
    
    def get_extensions(self):
        """Get all registered extensions."""
        return self.extensions
    
    def get_extension(self, name):
        """Get a specific extension by name."""
        for ext in self.extensions:
            if ext.get_name() == name:
                return ext
        return None


# Example usage in an extension:
"""
# my_custom_extension/extension.py

from study_framework_core.core.extension_base import DashboardExtension
from flask import Blueprint

class MyCustomExtension(DashboardExtension):
    
    def get_name(self):
        return "My Custom Extension"
    
    def get_version(self):
        return "1.0.0"
    
    def register_navigation(self):
        # Add a navigation item
        self.nav_registry.register_item({
            'label': 'My Feature',
            'icon': 'fas fa-star',
            'url': 'my_custom_feature',
            'url_for': True,
            'position': 35  # Position between existing items
        })
        
        # Add a user menu item
        self.nav_registry.register_user_menu_item({
            'label': 'My Settings',
            'icon': 'fas fa-cog',
            'url': 'my_settings',
            'url_for': True,
            'position': 10
        })
    
    def register_routes(self):
        # Create a blueprint for this extension
        bp = Blueprint('my_extension', __name__, 
                      url_prefix='/internal_web/my-extension')
        
        @bp.route('/feature')
        def my_custom_feature():
            return render_template('my_feature.html')
        
        self.app.register_blueprint(bp)
    
    def register_templates(self):
        import os
        return os.path.join(os.path.dirname(__file__), 'templates')
"""