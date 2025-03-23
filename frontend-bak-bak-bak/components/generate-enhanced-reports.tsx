// Simple utility function to download enhanced reports from the backend
// with fallback to client-side generation
const generateEnhancedReport = async (timeRange: string, toast: any): Promise<boolean> => {
  try {
    // Convert time range to date range
    const endDate = new Date().toISOString().split('T')[0]; // Today in YYYY-MM-DD format
    let startDate;
    
    switch (timeRange) {
      case 'week':
        startDate = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
        break;
      case 'month':
        startDate = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
        break;
      case 'year':
        startDate = new Date(Date.now() - 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
        break;
      default: // day
        startDate = new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
    }
    
    // Get auth token from localStorage with error handling
    let token = "";
    try {
      // Try different possible token storage locations
      const authToken = localStorage.getItem("authToken");
      const jwtToken = localStorage.getItem("jwtToken");
      const userStr = localStorage.getItem("currentUser");
      
      if (authToken) {
        token = authToken;
      } else if (jwtToken) {
        token = jwtToken;
      } else if (userStr) {
        const user = JSON.parse(userStr);
        token = user.token || "";
      }
    } catch (error) {
      console.error("Error accessing authentication token:", error);
    }
    
    // If no token, fall back to client-side generation
    if (!token) {
      console.warn("No authentication token found, falling back to client-side PDF generation");
      return false; // Signal to use fallback method
    }
    
    // Prepare the auth header
    const authHeader = token.startsWith('Bearer ') ? token : `Bearer ${token}`;
    
    // Call the backend API
    console.log(`Downloading report for ${startDate} to ${endDate}`);
    try {
      const response = await fetch(`/api/v1/reports/report?format=pdf&start_date=${startDate}&end_date=${endDate}`, {
        method: 'POST',
        headers: {
          'Authorization': authHeader,
          'Accept': 'application/octet-stream'
        },
      });
      
      if (!response.ok) {
        // If the API call fails, fall back to client-side generation
        console.warn(`API error: ${response.status}. Falling back to client-side PDF generation`);
        return false; // Signal to use fallback method
      }
      
      // Process the file download
      const blob = await response.blob();
      const fileURL = window.URL.createObjectURL(blob);
      const downloadLink = document.createElement('a');
      downloadLink.href = fileURL;
      downloadLink.download = `energy_report_${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(downloadLink);
      downloadLink.click();
      document.body.removeChild(downloadLink);
      
      if (toast) {
        toast({
          title: "Report Downloaded",
          description: "Your enhanced energy report has been downloaded.",
        });
      }
      
      return true; // Signal successful download
    } catch (fetchError) {
      console.error("Error fetching report:", fetchError);
      return false; // Signal to use fallback method
    }
    
  } catch (error) {
    console.error("Error in report generation:", error);
    // Fall back to client-side generation on any error
    return false; // Signal to use fallback method
  }
};

export default generateEnhancedReport;
