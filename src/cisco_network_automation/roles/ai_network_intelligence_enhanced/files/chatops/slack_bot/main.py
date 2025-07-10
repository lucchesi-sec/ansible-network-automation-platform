#!/usr/bin/env python3
"""
Slack Bot for AI Network Intelligence Platform
Provides ChatOps interface for ML model management and network automation
"""

import os
import json
import yaml
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import requests
from prometheus_client import Counter, Histogram, Gauge

from command_handler import CommandHandler
from ml_integration import MLIntegration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Prometheus metrics
command_counter = Counter('chatops_commands_total', 'Total number of ChatOps commands', ['command', 'status'])
command_duration = Histogram('chatops_command_duration_seconds', 'Command execution duration')
active_users = Gauge('chatops_active_users', 'Number of active ChatOps users')

class AINetworkSlackBot:
    """Main Slack Bot class for AI Network Intelligence platform"""
    
    def __init__(self):
        self.app = App(token=os.environ["SLACK_BOT_TOKEN"])
        self.command_handler = CommandHandler()
        self.ml_integration = MLIntegration()
        self.config = self._load_config()
        self.active_sessions = {}
        
        # Register event handlers
        self._register_handlers()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load ChatOps configuration"""
        try:
            with open('/etc/chatops/config.yaml', 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}
    
    def _register_handlers(self):
        """Register Slack event handlers"""
        
        @self.app.event("app_mention")
        def handle_app_mention(event, say, context):
            """Handle direct mentions of the bot"""
            user_id = event["user"]
            text = event["text"]
            channel_id = event["channel"]
            
            logger.info(f"App mention from {user_id}: {text}")
            
            # Extract command from mention
            bot_user_id = context["bot_user_id"]
            command_text = text.replace(f"<@{bot_user_id}>", "").strip()
            
            if not command_text:
                self._send_help_message(say, user_id)
                return
            
            # Process command
            self._process_command(command_text, user_id, channel_id, say)
        
        @self.app.command("/ai")
        def handle_ai_command(ack, respond, command):
            """Handle /ai slash commands"""
            ack()
            
            user_id = command["user_id"]
            text = command["text"]
            channel_id = command["channel_id"]
            
            logger.info(f"Slash command from {user_id}: /ai {text}")
            
            # Process command
            self._process_command(text, user_id, channel_id, respond)
        
        @self.app.action("model_deploy_confirm")
        def handle_model_deploy_confirm(ack, body, respond):
            """Handle model deployment confirmation"""
            ack()
            
            user_id = body["user"]["id"]
            action_value = json.loads(body["actions"][0]["value"])
            
            logger.info(f"Deploy confirmation from {user_id}: {action_value}")
            
            # Execute deployment
            result = self._execute_model_deployment(action_value, user_id)
            respond(result)
        
        @self.app.action("anomaly_investigate")
        def handle_anomaly_investigate(ack, body, respond):
            """Handle anomaly investigation action"""
            ack()
            
            user_id = body["user"]["id"]
            anomaly_id = body["actions"][0]["value"]
            
            logger.info(f"Anomaly investigation from {user_id}: {anomaly_id}")
            
            # Start investigation
            result = self._start_anomaly_investigation(anomaly_id, user_id)
            respond(result)
        
        @self.app.action("automation_approve")
        def handle_automation_approve(ack, body, respond):
            """Handle automation action approval"""
            ack()
            
            user_id = body["user"]["id"]
            action_data = json.loads(body["actions"][0]["value"])
            
            logger.info(f"Automation approval from {user_id}: {action_data}")
            
            # Execute automation
            result = self._execute_automation_action(action_data, user_id)
            respond(result)
    
    def _process_command(self, command_text: str, user_id: str, channel_id: str, respond_func):
        """Process incoming command"""
        with command_duration.time():
            try:
                # Parse command
                parts = command_text.strip().split()
                if not parts:
                    self._send_help_message(respond_func, user_id)
                    return
                
                command = parts[0].lower()
                args = parts[1:] if len(parts) > 1 else []
                
                # Check permissions
                if not self._check_permissions(user_id, command):
                    command_counter.labels(command=command, status='unauthorized').inc()
                    respond_func({
                        "text": f"❌ You don't have permission to execute `{command}` command.",
                        "response_type": "ephemeral"
                    })
                    return
                
                # Execute command
                result = self.command_handler.execute_command(command, args, user_id, channel_id)
                
                if result["success"]:
                    command_counter.labels(command=command, status='success').inc()
                else:
                    command_counter.labels(command=command, status='error').inc()
                
                # Send response
                respond_func(result["response"])
                
            except Exception as e:
                logger.error(f"Error processing command: {e}")
                command_counter.labels(command='unknown', status='error').inc()
                respond_func({
                    "text": f"❌ Error processing command: {str(e)}",
                    "response_type": "ephemeral"
                })
    
    def _check_permissions(self, user_id: str, command: str) -> bool:
        """Check if user has permission to execute command"""
        try:
            # Get user info from Slack
            user_info = self.app.client.users_info(user=user_id)
            user_email = user_info["user"]["profile"].get("email", "")
            
            # Load command permissions
            command_permissions = self._load_command_permissions()
            
            # Check command-specific permissions
            if command in command_permissions:
                required_roles = command_permissions[command].get("permissions", [])
                user_roles = self._get_user_roles(user_email)
                
                return any(role in user_roles for role in required_roles)
            
            # Default to viewer permissions for unknown commands
            return "viewer" in self._get_user_roles(user_email)
            
        except Exception as e:
            logger.error(f"Error checking permissions: {e}")
            return False
    
    def _load_command_permissions(self) -> Dict[str, Any]:
        """Load command permission definitions"""
        try:
            permissions = {}
            for file_name in ["model_management.json", "predictions.json", "automation.json"]:
                with open(f"/app/commands/{file_name}", "r") as f:
                    data = json.load(f)
                    for cmd in data["commands"]:
                        permissions[cmd["name"]] = cmd
            return permissions
        except Exception as e:
            logger.error(f"Error loading command permissions: {e}")
            return {}
    
    def _get_user_roles(self, user_email: str) -> List[str]:
        """Get user roles from identity provider or configuration"""
        # TODO: Integrate with actual identity provider (AD, LDAP, etc.)
        # For now, use simple mapping
        role_mapping = {
            "admin@company.com": ["ml_admin", "network_admin", "viewer"],
            "ml-engineer@company.com": ["ml_engineer", "viewer"],
            "netops@company.com": ["network_operator", "viewer"]
        }
        
        return role_mapping.get(user_email, ["viewer"])
    
    def _send_help_message(self, respond_func, user_id: str):
        """Send help message with available commands"""
        help_blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🤖 AI Network Intelligence - Available Commands"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Model Management:*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "• `/ai deploy model <name> <version>` - Deploy ML model\n"
                            "• `/ai status models [name]` - Show model status\n"
                            "• `/ai train <model> --dataset <data>` - Start training"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Predictions & Analytics:*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "• `/ai predict traffic --device <id>` - Traffic prediction\n"
                            "• `/ai analyze anomalies --severity <level>` - Anomaly analysis\n"
                            "• `/ai explain prediction <id>` - Prediction explanation"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Automation Control:*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "• `/ai automate enable <rule>` - Enable automation rule\n"
                            "• `/ai workflow run <name>` - Execute workflow\n"
                            "• `/ai dashboard <type>` - Show dashboard link"
                }
            }
        ]
        
        respond_func({
            "blocks": help_blocks,
            "response_type": "ephemeral"
        })
    
    def _execute_model_deployment(self, deployment_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Execute model deployment"""
        try:
            model_name = deployment_data["model_name"]
            version = deployment_data["version"]
            environment = deployment_data.get("environment", "staging")
            
            logger.info(f"Deploying {model_name} v{version} to {environment} by {user_id}")
            
            # Call ML API for deployment
            result = self.ml_integration.deploy_model(model_name, version, environment)
            
            if result["success"]:
                return {
                    "text": f"✅ Successfully deployed {model_name} v{version} to {environment}",
                    "blocks": [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"*Model Deployment Successful* ✅\n\n"
                                       f"*Model:* {model_name}\n"
                                       f"*Version:* {version}\n"
                                       f"*Environment:* {environment}\n"
                                       f"*Deployed by:* <@{user_id}>\n"
                                       f"*Deployment ID:* {result['deployment_id']}"
                            }
                        },
                        {
                            "type": "actions",
                            "elements": [
                                {
                                    "type": "button",
                                    "text": {
                                        "type": "plain_text",
                                        "text": "View Metrics"
                                    },
                                    "url": f"{self.config['chatops']['integrations']['grafana']}/d/model-metrics"
                                },
                                {
                                    "type": "button",
                                    "text": {
                                        "type": "plain_text",
                                        "text": "MLflow UI"
                                    },
                                    "url": f"{self.config['chatops']['integrations']['mlflow']}"
                                }
                            ]
                        }
                    ]
                }
            else:
                return {
                    "text": f"❌ Failed to deploy {model_name}: {result['error']}",
                    "response_type": "ephemeral"
                }
                
        except Exception as e:
            logger.error(f"Deployment error: {e}")
            return {
                "text": f"❌ Deployment failed: {str(e)}",
                "response_type": "ephemeral"
            }
    
    def _start_anomaly_investigation(self, anomaly_id: str, user_id: str) -> Dict[str, Any]:
        """Start anomaly investigation"""
        try:
            logger.info(f"Starting anomaly investigation {anomaly_id} by {user_id}")
            
            # Get anomaly details
            anomaly = self.ml_integration.get_anomaly_details(anomaly_id)
            
            if not anomaly:
                return {
                    "text": f"❌ Anomaly {anomaly_id} not found",
                    "response_type": "ephemeral"
                }
            
            # Start investigation workflow
            investigation = self.ml_integration.start_investigation(anomaly_id, user_id)
            
            return {
                "text": f"🔍 Investigation started for anomaly {anomaly_id}",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Anomaly Investigation Started* 🔍\n\n"
                                   f"*Anomaly ID:* {anomaly_id}\n"
                                   f"*Type:* {anomaly['type']}\n"
                                   f"*Severity:* {anomaly['severity']}\n"
                                   f"*Device:* {anomaly['device']}\n"
                                   f"*Investigator:* <@{user_id}>\n"
                                   f"*Investigation ID:* {investigation['id']}"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Root Cause Analysis:*\n{investigation['analysis']}"
                        }
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "View Details"
                                },
                                "url": f"{self.config['chatops']['integrations']['grafana']}/d/anomaly-analysis?anomaly={anomaly_id}"
                            },
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "Auto-Remediate"
                                },
                                "style": "primary",
                                "action_id": "auto_remediate",
                                "value": json.dumps({"anomaly_id": anomaly_id, "investigation_id": investigation['id']})
                            }
                        ]
                    }
                ]
            }
            
        except Exception as e:
            logger.error(f"Investigation error: {e}")
            return {
                "text": f"❌ Investigation failed: {str(e)}",
                "response_type": "ephemeral"
            }
    
    def _execute_automation_action(self, action_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Execute automation action"""
        try:
            action_type = action_data["action_type"]
            target = action_data["target"]
            parameters = action_data.get("parameters", {})
            
            logger.info(f"Executing automation {action_type} on {target} by {user_id}")
            
            # Execute automation
            result = self.ml_integration.execute_automation(action_type, target, parameters, user_id)
            
            if result["success"]:
                return {
                    "text": f"✅ Automation executed successfully",
                    "blocks": [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"*Automation Executed* ✅\n\n"
                                       f"*Action:* {action_type}\n"
                                       f"*Target:* {target}\n"
                                       f"*Executed by:* <@{user_id}>\n"
                                       f"*Execution ID:* {result['execution_id']}\n"
                                       f"*Status:* {result['status']}"
                            }
                        }
                    ]
                }
            else:
                return {
                    "text": f"❌ Automation failed: {result['error']}",
                    "response_type": "ephemeral"
                }
                
        except Exception as e:
            logger.error(f"Automation error: {e}")
            return {
                "text": f"❌ Automation failed: {str(e)}",
                "response_type": "ephemeral"
            }
    
    def send_notification(self, channel: str, notification: Dict[str, Any]):
        """Send notification to Slack channel"""
        try:
            self.app.client.chat_postMessage(
                channel=channel,
                **notification
            )
            logger.info(f"Notification sent to {channel}")
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
    
    def run(self):
        """Start the Slack bot"""
        logger.info("Starting AI Network Intelligence Slack Bot...")
        handler = SocketModeHandler(self.app, os.environ["SLACK_APP_TOKEN"])
        handler.start()

if __name__ == "__main__":
    bot = AINetworkSlackBot()
    bot.run()