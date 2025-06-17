from typing import Dict, List, Callable, Any
import re
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class TriggerType(Enum):
    SENDER_CONTAINS = "sender_contains"
    SUBJECT_CONTAINS = "subject_contains"
    BODY_CONTAINS = "body_contains"
    SENDER_EXACT = "sender_exact"
    SUBJECT_REGEX = "subject_regex"
    ATTACHMENT_EXISTS = "attachment_exists"
    TIME_RANGE = "time_range"


@dataclass
class TriggerRule:
    id: str
    user_id: int
    trigger_type: TriggerType
    condition: str
    action: str
    is_active: bool = True
    metadata: Dict = None


@dataclass
class TriggerContext:
    user_id: int
    provider_id: int
    message_data: Dict
    timestamp: datetime


class TriggerHandler:
    def __init__(self):
        self.rules: Dict[int, List[TriggerRule]] = {}
        self.action_handlers: Dict[str, Callable] = {
            "log_message": self._log_message,
            "mark_as_read": self._mark_as_read,
            "forward_email": self._forward_email,
            "send_notification": self._send_notification,
            "webhook_call": self._webhook_call,
            "custom_script": self._custom_script,
        }
    
    def add_rule(self, rule: TriggerRule):
        """Add a trigger rule for a user"""
        if rule.user_id not in self.rules:
            self.rules[rule.user_id] = []
        self.rules[rule.user_id].append(rule)
    
    def remove_rule(self, user_id: int, rule_id: str):
        """Remove a trigger rule"""
        if user_id in self.rules:
            self.rules[user_id] = [
                rule for rule in self.rules[user_id] 
                if rule.id != rule_id
            ]
    
    def handle_new_email(self, user_id: int, provider_id: int, message_data: Dict):
        """Process a new email against all trigger rules for a user"""
        if user_id not in self.rules:
            return
        
        context = TriggerContext(
            user_id=user_id,
            provider_id=provider_id,
            message_data=message_data,
            timestamp=datetime.now()
        )
        
        for rule in self.rules[user_id]:
            if rule.is_active and self._evaluate_rule(rule, context):
                self._execute_action(rule, context)
    
    def _evaluate_rule(self, rule: TriggerRule, context: TriggerContext) -> bool:
        """Evaluate if a trigger rule matches the email"""
        message = context.message_data
        
        try:
            if rule.trigger_type == TriggerType.SENDER_CONTAINS:
                return rule.condition.lower() in message.get('sender', '').lower()
            
            elif rule.trigger_type == TriggerType.SUBJECT_CONTAINS:
                return rule.condition.lower() in message.get('subject', '').lower()
            
            elif rule.trigger_type == TriggerType.BODY_CONTAINS:
                body = message.get('body', '') + message.get('html_body', '')
                return rule.condition.lower() in body.lower()
            
            elif rule.trigger_type == TriggerType.SENDER_EXACT:
                return rule.condition.lower() == message.get('sender', '').lower()
            
            elif rule.trigger_type == TriggerType.SUBJECT_REGEX:
                pattern = re.compile(rule.condition, re.IGNORECASE)
                return bool(pattern.search(message.get('subject', '')))
            
            elif rule.trigger_type == TriggerType.ATTACHMENT_EXISTS:
                attachments = message.get('attachments', [])
                return len(attachments) > 0
            
            elif rule.trigger_type == TriggerType.TIME_RANGE:
                # Expected format: "09:00-17:00"
                time_range = rule.condition.split('-')
                if len(time_range) == 2:
                    start_time = datetime.strptime(time_range[0], "%H:%M").time()
                    end_time = datetime.strptime(time_range[1], "%H:%M").time()
                    current_time = context.timestamp.time()
                    return start_time <= current_time <= end_time
            
            return False
        
        except Exception as e:
            print(f"Error evaluating rule {rule.id}: {e}")
            return False
    
    def _execute_action(self, rule: TriggerRule, context: TriggerContext):
        """Execute the action for a triggered rule"""
        try:
            action_handler = self.action_handlers.get(rule.action)
            if action_handler:
                action_handler(rule, context)
            else:
                print(f"Unknown action: {rule.action}")
        
        except Exception as e:
            print(f"Error executing action {rule.action}: {e}")
    
    def _log_message(self, rule: TriggerRule, context: TriggerContext):
        """Log the email message"""
        message = context.message_data
        print(f"[TRIGGER {rule.id}] Email matched:")
        print(f"  From: {message.get('sender')}")
        print(f"  Subject: {message.get('subject')}")
        print(f"  Received: {message.get('received_at')}")
    
    def _mark_as_read(self, rule: TriggerRule, context: TriggerContext):
        """Mark the email as read"""
        # This would integrate with the email provider to mark as read
        print(f"[TRIGGER {rule.id}] Marking email as read: {context.message_data.get('id')}")
    
    def _forward_email(self, rule: TriggerRule, context: TriggerContext):
        """Forward the email to specified address"""
        forward_to = rule.metadata.get('forward_to') if rule.metadata else None
        if forward_to:
            print(f"[TRIGGER {rule.id}] Forwarding email to: {forward_to}")
        else:
            print(f"[TRIGGER {rule.id}] No forward address specified")
    
    def _send_notification(self, rule: TriggerRule, context: TriggerContext):
        """Send a notification (email, SMS, push, etc.)"""
        notification_type = rule.metadata.get('type', 'email') if rule.metadata else 'email'
        recipient = rule.metadata.get('recipient') if rule.metadata else None
        
        message = context.message_data
        notification_text = f"New email from {message.get('sender')}: {message.get('subject')}"
        
        print(f"[TRIGGER {rule.id}] Sending {notification_type} notification to {recipient}")
        print(f"  Content: {notification_text}")
    
    def _webhook_call(self, rule: TriggerRule, context: TriggerContext):
        """Call a webhook URL with email data"""
        webhook_url = rule.metadata.get('url') if rule.metadata else None
        if webhook_url:
            print(f"[TRIGGER {rule.id}] Calling webhook: {webhook_url}")
            # This would make an HTTP POST request to the webhook URL
        else:
            print(f"[TRIGGER {rule.id}] No webhook URL specified")
    
    def _custom_script(self, rule: TriggerRule, context: TriggerContext):
        """Execute a custom script"""
        script_path = rule.metadata.get('script_path') if rule.metadata else None
        if script_path:
            print(f"[TRIGGER {rule.id}] Executing custom script: {script_path}")
            # This would execute the custom script with email data as parameters
        else:
            print(f"[TRIGGER {rule.id}] No script path specified")


# Example usage and predefined rules
def create_sample_rules() -> List[TriggerRule]:
    """Create some sample trigger rules"""
    return [
        TriggerRule(
            id="rule_1",
            user_id=1,
            trigger_type=TriggerType.SENDER_CONTAINS,
            condition="boss@company.com",
            action="send_notification",
            metadata={"type": "push", "recipient": "user@phone.com"}
        ),
        TriggerRule(
            id="rule_2",
            user_id=1,
            trigger_type=TriggerType.SUBJECT_CONTAINS,
            condition="urgent",
            action="forward_email",
            metadata={"forward_to": "urgent@company.com"}
        ),
        TriggerRule(
            id="rule_3",
            user_id=1,
            trigger_type=TriggerType.ATTACHMENT_EXISTS,
            condition="",
            action="log_message"
        ),
        TriggerRule(
            id="rule_4",
            user_id=1,
            trigger_type=TriggerType.TIME_RANGE,
            condition="18:00-08:00",
            action="webhook_call",
            metadata={"url": "https://api.company.com/after-hours-email"}
        )
    ]