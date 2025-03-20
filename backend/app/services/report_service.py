"""
Service for energy report generation and management.
"""
import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple

from app.db.data import us_c, d_c, an_c, r_c, u_c
from app.models.report import ReportDB, ReportStatus, ReportFormat
from app.utils.report.report_generator import EnergyReportGenerator, generate_energy_report


class ReportService:
    """
    Service for managing energy report generation and storage.
    """
    
    @staticmethod
    def create_report(report_data: ReportDB) -> str:
        """
        Create a report record in the database.
        
        Args:
            report_data: Report data to store
            
        Returns:
            str: ID of the created report
        """
        report_dict = report_data.model_dump()
        result = r_c.insert_one(report_dict)
        return str(result.inserted_id)
    
    @staticmethod
    def get_report(report_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a report by ID.
        
        Args:
            report_id: ID of the report to retrieve
            
        Returns:
            Optional[Dict]: Report data if found, None otherwise
        """
        report = r_c.find_one({"id": report_id})
        return report
    
    @staticmethod
    def get_user_reports(user_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve all reports for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            List[Dict]: List of report data
        """
        cursor = r_c.find({"user_id": user_id}).sort("created", -1)
        reports = list(cursor)  # Convert cursor to list
        return reports
    
    @staticmethod
    def update_report_status(report_id: str, status: ReportStatus, **kwargs) -> bool:
        """
        Update the status of a report.
        
        Args:
            report_id: ID of the report to update
            status: New status
            **kwargs: Additional fields to update
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        update_data = {"status": status, "updated": datetime.utcnow()}
        update_data.update(kwargs)
        
        result = r_c.update_one(
            {"id": report_id},
            {"$set": update_data}
        )
        
        return result.modified_count > 0
    
    @staticmethod
    def fetch_energy_data(
        user_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        device_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch energy usage data from the database.
        
        Args:
            user_id: ID of the user
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            device_ids: List of device IDs to filter by
            
        Returns:
            List[Dict]: List of energy usage records
        """
        # Convert string dates to datetime objects if provided
        start_datetime = None
        end_datetime = None
        
        if start_date:
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
        
        if end_date:
            # Set end_datetime to the end of the day
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d")
            end_datetime = end_datetime.replace(hour=23, minute=59, second=59)
        
        # Build the query
        query = {}
        
        # Get all devices owned by the user
        if device_ids:
            query["device_id"] = {"$in": device_ids}
        else:
            # If no specific devices are requested, get all devices for the user
            user_devices = list(d_c.find({"user_id": user_id}))
            if not user_devices:
                return []  # User has no devices, return empty list
            
            user_device_ids = [device["id"] for device in user_devices]
            
            if user_device_ids:
                query["device_id"] = {"$in": user_device_ids}
            else:
                # If user has no devices, return empty list
                return []
        
        # Add date range filter if provided
        if start_datetime or end_datetime:
            timestamp_query = {}
            if start_datetime:
                timestamp_query["$gte"] = start_datetime
            if end_datetime:
                timestamp_query["$lte"] = end_datetime
                
            if timestamp_query:
                query["timestamp"] = timestamp_query
        
        # Execute the query
        print(f"Query: {query}")
        cursor = us_c.find(query).sort("timestamp", 1)
        print(f"Cursor type: {type(cursor)}")
        usage_data = list(cursor)  # Convert cursor to list
        print(f"Usage data type: {type(usage_data)}, length: {len(usage_data)}")
        
        # Enhance usage data with device information
        enhanced_data = []
        for record in usage_data:
            # Get device info
            device_id = record.get("device_id")
            device = d_c.find_one({"id": device_id})
            
            # Create enhanced record with location
            enhanced_record = {
                "timestamp": record.get("timestamp").isoformat() if isinstance(record.get("timestamp"), datetime) else record.get("timestamp"),
                "device_id": device_id,
                "energy_consumed": record.get("energy_consumed", 0),
                "location": device.get("room_id") if device else "Unknown"
            }
            
            enhanced_data.append(enhanced_record)
        
        return enhanced_data
    
    @staticmethod
    def fetch_user_data(user_id: str) -> Dict[str, Any]:
        """
        Fetch user data for report personalization.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Dict: User data
        """
        user = u_c.find_one({"id": user_id})
        
        if not user:
            return {}
        
        return {
            "email": user.get("email"),
            "username": user.get("username")
        }
    
    @staticmethod
    def generate_report(report_id: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Generate a report based on its ID.
        
        Args:
            report_id: ID of the report to generate
            
        Returns:
            Tuple[bool, Optional[str], Optional[str]]: 
                - Success flag
                - File path if successful
                - Error message if failed
        """
        # Get report data
        report_data = ReportService.get_report(report_id)
        if not report_data:
            return False, None, "Report not found"
        
        try:
            # Update status to generating
            ReportService.update_report_status(
                report_id, 
                ReportStatus.GENERATING
            )
            
            # Fetch energy data
            energy_data = ReportService.fetch_energy_data(
                user_id=report_data["user_id"],
                start_date=report_data.get("start_date"),
                end_date=report_data.get("end_date"),
                device_ids=report_data.get("device_ids")
            )
            
            if not energy_data:
                error_msg = "No energy data found for the specified criteria"
                ReportService.update_report_status(
                    report_id, 
                    ReportStatus.FAILED,
                    error_message=error_msg
                )
                return False, None, error_msg
            
            # Fetch user data for personalization
            user_data = ReportService.fetch_user_data(report_data["user_id"])
            
            # Generate the report
            report_path = generate_energy_report(
                energy_data=energy_data,
                user_data=user_data,
                format=report_data["format"].lower(),
                start_date=report_data.get("start_date"),
                end_date=report_data.get("end_date")
            )
            
            # Calculate some basic stats for metadata
            total_energy = sum(record.get("energy_consumed", 0) for record in energy_data)
            device_count = len(set(record.get("device_id") for record in energy_data))
            
            # Update the report record with success status
            ReportService.update_report_status(
                report_id,
                ReportStatus.COMPLETED,
                file_path=report_path,
                completed=datetime.utcnow(),
                metadata={
                    "total_energy": total_energy,
                    "record_count": len(energy_data),
                    "device_count": device_count,
                    "file_size": os.path.getsize(report_path) if os.path.exists(report_path) else 0
                }
            )
            
            return True, report_path, None
            
        except Exception as e:
            # Update the report record with failure status
            error_message = str(e)
            ReportService.update_report_status(
                report_id,
                ReportStatus.FAILED,
                error_message=error_message
            )
            
            return False, None, error_message

    @staticmethod
    def delete_report(report_id: str) -> bool:
        """
        Delete a report record from the database.
        
        Args:
            report_id: ID of the report to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        result = r_c.delete_one({"id": report_id})
        return result.deleted_count > 0
