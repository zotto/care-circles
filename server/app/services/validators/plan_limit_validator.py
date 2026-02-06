"""
Plan Limit Validator

Validates plan creation limits and constraints for users.
"""

import logging
from typing import Optional
from fastapi import HTTPException, status

from app.config.constants import PlanLimitConstants
from app.db.repositories.care_plan_repository import CarePlanRepository

logger = logging.getLogger(__name__)


class PlanLimitValidator:
    """
    Validator for enforcing plan creation limits
    
    This class provides atomic validation logic for plan limits,
    ensuring users don't exceed their maximum allowed open plans.
    """
    
    def __init__(self, plan_repository: CarePlanRepository):
        """
        Initialize the plan limit validator
        
        Args:
            plan_repository: Repository for plan data access
        """
        self.plan_repo = plan_repository
        self.max_open_plans = PlanLimitConstants.MAX_OPEN_PLANS_PER_USER
    
    def validate_can_create_plan(self, user_id: str) -> None:
        """
        Validate that a user can create a new plan
        
        Checks if the user has reached their maximum open plans limit.
        Open plans include those with 'draft' or 'approved' status.
        
        Args:
            user_id: User ID to validate
            
        Raises:
            HTTPException: If user has reached the maximum open plans limit
        """
        try:
            open_plan_count = self.plan_repo.count_open_plans_by_creator(user_id)
            
            if open_plan_count >= self.max_open_plans:
                logger.warning(
                    f"User {user_id} attempted to create plan but has reached limit "
                    f"({open_plan_count}/{self.max_open_plans})"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"You have reached the maximum of {self.max_open_plans} open plans. "
                        "Please complete or archive an existing plan before creating a new one."
                    )
                )
            
            logger.debug(
                f"User {user_id} can create plan ({open_plan_count}/{self.max_open_plans})"
            )
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error validating plan limit for user {user_id}: {str(e)}")
            raise
    
    def get_remaining_plan_slots(self, user_id: str) -> int:
        """
        Get the number of remaining plan slots for a user
        
        Args:
            user_id: User ID
            
        Returns:
            int: Number of remaining plan slots (0 if at or over limit)
        """
        try:
            open_plan_count = self.plan_repo.count_open_plans_by_creator(user_id)
            remaining = max(0, self.max_open_plans - open_plan_count)
            
            logger.debug(f"User {user_id} has {remaining} remaining plan slots")
            return remaining
        
        except Exception as e:
            logger.error(f"Error getting remaining plan slots for user {user_id}: {str(e)}")
            raise
    
    def get_plan_limit_info(self, user_id: str) -> dict:
        """
        Get comprehensive plan limit information for a user
        
        Args:
            user_id: User ID
            
        Returns:
            dict: Dictionary containing:
                - open_plans: Number of open plans
                - max_plans: Maximum allowed open plans
                - remaining_slots: Number of remaining plan slots
                - can_create: Whether user can create a new plan
        """
        try:
            open_plan_count = self.plan_repo.count_open_plans_by_creator(user_id)
            remaining = max(0, self.max_open_plans - open_plan_count)
            can_create = open_plan_count < self.max_open_plans
            
            return {
                "open_plans": open_plan_count,
                "max_plans": self.max_open_plans,
                "remaining_slots": remaining,
                "can_create": can_create
            }
        
        except Exception as e:
            logger.error(f"Error getting plan limit info for user {user_id}: {str(e)}")
            raise
