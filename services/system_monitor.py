"""System monitoring service for GreenOps"""

import psutil
import time
from datetime import datetime, timedelta


class SystemMonitor:
    """Monitor laptop/server resources for GreenOps"""
    
    def __init__(self):
        self.start_time = datetime.utcnow()
    
    def get_cpu_usage(self):
        """Get current CPU usage percentage"""
        return psutil.cpu_percent(interval=1)
    
    def get_memory_usage(self):
        """Get memory usage information"""
        memory = psutil.virtual_memory()
        return {
            'percent': memory.percent,
            'used_gb': memory.used / (1024**3),
            'total_gb': memory.total / (1024**3),
            'available_gb': memory.available / (1024**3)
        }
    
    def get_disk_usage(self):
        """Get disk usage information"""
        disk = psutil.disk_usage('/')
        return {
            'percent': disk.percent,
            'used_gb': disk.used / (1024**3),
            'total_gb': disk.total / (1024**3),
            'free_gb': disk.free / (1024**3)
        }
    
    def get_server_uptime(self):
        """Get server running time"""
        uptime = datetime.utcnow() - self.start_time
        return {
            'seconds': int(uptime.total_seconds()),
            'formatted': self._format_uptime(uptime)
        }
    
    def get_energy_level(self):
        """Calculate energy awareness level"""
        cpu = self.get_cpu_usage()
        memory = self.get_memory_usage()
        disk = self.get_disk_usage()
        
        # Calculate average usage
        avg_usage = (cpu + memory['percent'] + disk['percent']) / 3
        
        if avg_usage < 50:
            return 'green', 'Low Usage - Eco Friendly! 🌱'
        elif avg_usage < 75:
            return 'yellow', 'Medium Usage - Consider Optimization'
        else:
            return 'red', 'High Usage - Action Required! ⚠️'
    
    def get_battery_info(self):
        """Get battery status if available"""
        try:
            battery = psutil.sensors_battery()
            if battery:
                return {
                    'percent': battery.percent,
                    'plugged': battery.power_plugged,
                    'time_left': battery.secsleft if battery.secsleft != psutil.POWER_TIME_UNLIMITED else None
                }
        except:
            pass
        return None
    
    def get_resource_alerts(self):
        """Get resource usage alerts"""
        alerts = []
        
        cpu = self.get_cpu_usage()
        if cpu > 80:
            alerts.append({
                'type': 'warning',
                'message': f'High CPU usage detected ({cpu:.1f}%)'
            })
        
        memory = self.get_memory_usage()
        if memory['percent'] > 85:
            alerts.append({
                'type': 'warning',
                'message': f'High memory usage ({memory["percent"]:.1f}%)'
            })
        
        disk = self.get_disk_usage()
        if disk['percent'] > 80:
            alerts.append({
                'type': 'danger',
                'message': f'Storage almost full ({disk["percent"]:.1f}%)'
            })
        
        # Check battery
        battery = self.get_battery_info()
        if battery and not battery['plugged'] and battery['percent'] < 20:
            alerts.append({
                'type': 'warning',
                'message': 'Low battery - Enable Eco Mode to save power'
            })
        
        return alerts
    
    def get_idle_time(self):
        """Get system idle time (simplified)"""
        # This is a simplified version
        # In production, you'd track last user activity
        return 0
    
    def should_suggest_shutdown(self, idle_minutes=30):
        """Check if should suggest server shutdown"""
        idle_time = self.get_idle_time()
        return idle_time > (idle_minutes * 60)
    
    def get_system_summary(self):
        """Get complete system status summary"""
        cpu = self.get_cpu_usage()
        memory = self.get_memory_usage()
        disk = self.get_disk_usage()
        uptime = self.get_server_uptime()
        energy_level, energy_message = self.get_energy_level()
        battery = self.get_battery_info()
        alerts = self.get_resource_alerts()
        
        return {
            'cpu': {
                'percent': cpu,
                'status': self._get_status_color(cpu)
            },
            'memory': {
                'percent': memory['percent'],
                'used_gb': round(memory['used_gb'], 2),
                'total_gb': round(memory['total_gb'], 2),
                'status': self._get_status_color(memory['percent'])
            },
            'disk': {
                'percent': disk['percent'],
                'used_gb': round(disk['used_gb'], 2),
                'total_gb': round(disk['total_gb'], 2),
                'free_gb': round(disk['free_gb'], 2),
                'status': self._get_status_color(disk['percent'])
            },
            'uptime': uptime,
            'energy_level': energy_level,
            'energy_message': energy_message,
            'battery': battery,
            'alerts': alerts,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def calculate_energy_score(self, user_stats):
        """Calculate energy efficiency score (0-100)"""
        score = 100
        
        # CPU usage penalty
        cpu = self.get_cpu_usage()
        if cpu > 80:
            score -= 20
        elif cpu > 60:
            score -= 10
        
        # Memory usage penalty
        memory = self.get_memory_usage()
        if memory['percent'] > 85:
            score -= 15
        elif memory['percent'] > 70:
            score -= 8
        
        # Disk usage penalty
        disk = self.get_disk_usage()
        if disk['percent'] > 90:
            score -= 15
        elif disk['percent'] > 80:
            score -= 8
        
        # Bonus for eco mode
        if user_stats.get('eco_mode_enabled'):
            score += 10
        
        # Bonus for low uptime (efficient usage)
        uptime_hours = self.get_server_uptime()['seconds'] / 3600
        if uptime_hours < 2:
            score += 5
        
        return max(0, min(100, score))
    
    def _get_status_color(self, percentage):
        """Get status color based on percentage"""
        if percentage < 50:
            return 'success'
        elif percentage < 75:
            return 'warning'
        else:
            return 'danger'
    
    def _format_uptime(self, uptime):
        """Format uptime duration"""
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if seconds > 0 or not parts:
            parts.append(f"{seconds}s")
        
        return " ".join(parts)
    
    def get_eco_recommendations(self, user_id):
        """Get intelligent eco recommendations"""
        recommendations = []
        
        cpu = self.get_cpu_usage()
        memory = self.get_memory_usage()
        disk = self.get_disk_usage()
        battery = self.get_battery_info()
        
        # High CPU recommendation
        if cpu > 70:
            recommendations.append({
                'priority': 'high',
                'icon': 'fa-microchip',
                'message': f'High CPU usage ({cpu:.1f}%). Close unused applications.',
                'action': 'optimize'
            })
        
        # High memory recommendation
        if memory['percent'] > 80:
            recommendations.append({
                'priority': 'high',
                'icon': 'fa-memory',
                'message': f'High memory usage ({memory["percent"]:.1f}%). Restart server to free resources.',
                'action': 'restart'
            })
        
        # Disk space recommendation
        if disk['percent'] > 80:
            recommendations.append({
                'priority': 'high',
                'icon': 'fa-hdd',
                'message': f'Disk almost full ({disk["percent"]:.1f}%). Clean up old files.',
                'action': 'cleanup'
            })
        
        # Battery recommendation
        if battery and not battery['plugged']:
            recommendations.append({
                'priority': 'medium',
                'icon': 'fa-battery-half',
                'message': 'Running on battery. Enable Eco Mode to save power.',
                'action': 'eco_mode'
            })
        
        # Idle recommendation
        uptime_hours = self.get_server_uptime()['seconds'] / 3600
        if uptime_hours > 4:
            recommendations.append({
                'priority': 'low',
                'icon': 'fa-clock',
                'message': f'Server running for {uptime_hours:.1f} hours. Consider stopping when not in use.',
                'action': 'shutdown'
            })
        
        return recommendations


# Global instance
system_monitor = SystemMonitor()
