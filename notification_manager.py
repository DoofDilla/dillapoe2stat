"""
Notification Manager for PoE Stats Tracker
Handles all toast notifications with template system
"""

from win11toast import notify
from price_check_poe2 import fmt
from notification_templates import NotificationTemplates


class NotificationManager:
    """Manages all toast notifications for the PoE Stats Tracker"""
    
    def __init__(self, config, templates=None):
        self.config = config
        self.templates = templates or NotificationTemplates()
    
    def _format_time(self, seconds):
        """Format seconds into a readable time string"""
        if seconds is None:
            return "N/A"
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m {secs}s"
    
    def _get_icon_config(self, icon_type=None):
        """Get the notification icon configuration
        
        Args:
            icon_type: Type of icon ('pre_map', 'post_map', 'waystone', 'automode', or None for default)
        """
        return {
            'src': f'file://{self.config.get_icon_path(icon_type)}',
            'placement': 'appLogoOverride'
        }
    
    def _format_currency(self, value):
        """Format currency value for display in notifications (1 decimal place)"""
        if value is None or value <= 0.01:
            return "0"
        # Use 1 decimal place for notifications to keep them concise
        return fmt(value, prec=1)
    
    def _format_time_duration(self, seconds):
        """Format time duration for notifications"""
        if seconds is None:
            return "N/A"
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"
    
    def notify_from_template(self, template_key, icon_type=None, **values):
        """Create notification from template with provided values
        
        Args:
            template_key: Key for the notification template
            icon_type: Type of icon to use ('pre_map', 'post_map', 'waystone', 'automode')
            **values: Template values
        """
        if not self.config.NOTIFICATION_ENABLED:
            return
        
        template = getattr(self.templates, template_key, None)
        if not template:
            print(f"Warning: Template '{template_key}' not found")
            return
        
        # Add system values
        values['app_name'] = self.config.APP_NAME
        values['app_version'] = self.config.VERSION
        
        # Add currency icon to values
        values['currency_icon'] = self.templates.CURRENCY_ICON
        values['currency_suffix'] = self.templates.CURRENCY_SUFFIX
        
        try:
            title = template['title'].format(**values)
            message = template['template'].format(**values)
            notify(
                title, 
                message, 
                icon=self._get_icon_config(icon_type),
                app_id=self.config.TOAST_APP_ID  # Use stable ID (no version pollution)
            )
        except KeyError as e:
            print(f"Warning: Missing template value {e} for template '{template_key}'")
        except Exception as e:
            print(f"Warning: Failed to send notification '{template_key}': {e}")
    
    def get_template_variables(self, game_state):
        """Extract template variables from game state for overlay/notifications
        
        This method provides the same 40+ template variables used by notifications,
        enabling zero-duplication between notification templates and overlay templates.
        
        Args:
            game_state: Game state object with data
            
        Returns:
            dict: Template variables with formatted values
        """
        # Get base data from game state (should already include calculated values)
        values = game_state.get_notification_data()
        
        # Add formatted values only - no business logic here
        values.update({
            # Map formatting
            'map_value_fmt': self._format_currency(values['map_value']),
            'map_runtime_fmt': self._format_time_duration(values['map_runtime']),
            'map_value_per_hour_fmt': self._format_currency(values['map_value_per_hour']),   # ex/h for this map
            
            # Session formatting (using existing calculated values)
            'session_total_value_fmt': self._format_currency(values['session_total_value']),
            'session_avg_value_fmt': self._format_currency(values['session_avg_value']),     # ex/map
            'session_avg_time_fmt': self._format_time_duration(values['session_avg_time'] * 60 if values['session_avg_time'] else 0),  # min to seconds
            'session_maps_per_hour_fmt': f"{values['session_maps_per_hour']:.1f}",           # maps/h
            'session_value_per_hour_fmt': self._format_currency(values['session_value_per_hour']),  # ex/h
            'session_value_per_hour_before_fmt': self._format_currency(values['session_value_per_hour_before']),  # ex/h BEFORE current map
            
            # Drop value formatting (current map)
            'map_drop_1_value_fmt': self._format_currency(values['map_drop_1_value']),
            'map_drop_2_value_fmt': self._format_currency(values['map_drop_2_value']),
            'map_drop_3_value_fmt': self._format_currency(values['map_drop_3_value']),
            
            # Drop value formatting (last map)
            'last_map_drop_1_value_fmt': self._format_currency(values['last_map_drop_1_value']),
            'last_map_drop_2_value_fmt': self._format_currency(values['last_map_drop_2_value']),
            'last_map_drop_3_value_fmt': self._format_currency(values['last_map_drop_3_value']),
            
            # Drop value formatting (session cumulative)
            'session_drop_1_value_fmt': self._format_currency(values['session_drop_1_value']),
            'session_drop_2_value_fmt': self._format_currency(values['session_drop_2_value']),
            'session_drop_3_value_fmt': self._format_currency(values['session_drop_3_value']),
            
            # Best map formatting
            'best_map_value_fmt': self._format_currency(values['best_map_value']),
        })
        
        return values
    
    def notify_from_game_state(self, template_key, game_state, icon_type=None, **extra_values):
        """Create notification from template using game state data
        
        Args:
            template_key: Key for the notification template
            game_state: Game state object with data
            icon_type: Type of icon to use ('pre_map', 'post_map', 'waystone', 'automode')
            **extra_values: Additional template values
        """
        if not self.config.NOTIFICATION_ENABLED:
            return
        
        # Get template variables (reuses get_template_variables logic)
        values = self.get_template_variables(game_state)
        
        # Add any extra values provided
        values.update(extra_values)
        
        self.notify_from_template(template_key, icon_type=icon_type, **values)
    
    def notify_startup(self, session_info):
        """Create notification for application startup"""
        self.notify_from_template('STARTUP', 
            character=self.config.CHAR_TO_CHECK,
            session_id_short=session_info["session_id"][:8]
        )
    
    def notify_pre_map(self, game_state):
        """Create notification for PRE-map snapshot using game state"""
        self.notify_from_game_state('PRE_MAP', game_state, icon_type='pre_map')
    
    def notify_post_map(self, game_state):
        """Create notification for POST-map completion using game state"""
        self.notify_from_game_state('POST_MAP', game_state, icon_type='post_map')
    
    def notify_experimental_pre_map(self, game_state):
        """Create notification for experimental PRE-map snapshot using game state"""
        self.notify_from_game_state('EXPERIMENTAL_PRE_MAP', game_state, icon_type='waystone')
    
    def notify_inventory_check(self, inventory_items):
        """Create notification for inventory check"""
        if not self.config.NOTIFICATION_ENABLED:
            return
        
        try:
            from price_check_poe2 import valuate_items_raw
            rows, (total_c, total_e) = valuate_items_raw(inventory_items)
            
            valuable_items = [r for r in rows if (r['chaos_total'] or 0) > 0.01 or (r['ex_total'] or 0) > 0.01]
            total_items = len([r for r in rows if r['qty'] > 0])
            
            if total_e and total_e > 0.01:
                value_str = f"{self._format_currency(total_e)}ex"
            elif total_c and total_c > 0.01:
                value_str = f"{self._format_currency(total_c)}c"
            else:
                value_str = "0c"
            
            self.notify_from_template('INVENTORY_CHECK',
                total_items=total_items,
                valuable_items=len(valuable_items),
                inventory_value=value_str
            )
        except Exception:
            self.notify_from_template('INVENTORY_CHECK',
                total_items="?",
                valuable_items="?",
                inventory_value="?"
            )
    
    def notify_session_start(self, session_info):
        """Create notification for new session start"""
        self.notify_from_template('NEW_SESSION',
            character=self.config.CHAR_TO_CHECK,
            session_id_short=session_info["session_id"][:8],
            start_time=session_info["start_time_str"]
        )
    
    def notify_info(self, title, message):
        """Create generic info notification"""
        self.notify_from_template('INFO', title=title, message=message)
    
    # New notification methods using templates
    def notify_high_value_loot(self, item_name, item_value, game_state):
        """Notify about high-value loot found"""
        self.notify_from_game_state('HIGH_VALUE_LOOT', game_state,
            item_name=item_name,
            item_value=self._format_currency(item_value)
        )
    
    def notify_session_milestone(self, milestone_type, milestone_value, game_state):
        """Notify about session milestones (e.g., 10 maps, 100ex value)"""
        self.notify_from_game_state('SESSION_MILESTONE', game_state,
            milestone_type=milestone_type,
            milestone_value=milestone_value
        )
    
    def notify_automode(self, title, message):
        """Create notification for automode activities"""
        self.notify_from_template('INFO', icon_type='automode', title=title, message=message)