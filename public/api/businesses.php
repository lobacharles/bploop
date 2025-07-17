<?php
header('Content-Type: application/json');
require_once '../../src/config/database.php';

class BusinessAPI {
    private $conn;
    private $db;

    public function __construct() {
        $this->db = new Database();
        $this->conn = $this->db->getConnection();
    }

    public function getBusinesses($type = null) {
        try {
            $query = "SELECT * FROM businesses WHERE 1=1";
            $params = [];

            if ($type) {
                $query .= " AND business_type = ?";
                $params[] = $type;
            }

            $query .= " ORDER BY business_trade_name ASC";
            
            $stmt = $this->conn->prepare($query);
            if (!empty($params)) {
                $stmt->execute($params);
            } else {
                $stmt->execute();
            }

            $businesses = $stmt->fetchAll(PDO::FETCH_ASSOC);
            return $this->formatResponse(true, $businesses);
        } catch (PDOException $e) {
            return $this->formatResponse(false, null, $e->getMessage());
        }
    }

    public function getBusinessById($id) {
        try {
            $query = "SELECT b.*, 
                     (SELECT revenue FROM business_metrics 
                      WHERE business_id = b.id 
                      ORDER BY metric_date DESC LIMIT 1) as current_revenue,
                     (SELECT predicted_revenue FROM business_predictions 
                      WHERE business_id = b.id 
                      ORDER BY prediction_date DESC LIMIT 1) as predicted_revenue
                     FROM businesses b 
                     WHERE b.id = ?";
            
            $stmt = $this->conn->prepare($query);
            $stmt->execute([$id]);
            
            $business = $stmt->fetch(PDO::FETCH_ASSOC);
            
            if ($business) {
                // Calculate growth prediction
                if ($business['current_revenue'] && $business['predicted_revenue']) {
                    $growth = (($business['predicted_revenue'] - $business['current_revenue']) 
                             / $business['current_revenue']) * 100;
                    $business['growth_prediction'] = round($growth, 2);
                } else {
                    $business['growth_prediction'] = 0;
                }
                
                return $this->formatResponse(true, $business);
            }
            
            return $this->formatResponse(false, null, "Business not found");
        } catch (PDOException $e) {
            return $this->formatResponse(false, null, $e->getMessage());
        }
    }

    public function getBusinessStats() {
        try {
            $stats = [
                'total_businesses' => 0,
                'by_type' => [],
                'by_year' => [],
                'by_barangay' => []
            ];

            // Total businesses
            $query = "SELECT COUNT(*) as total FROM businesses";
            $stmt = $this->conn->query($query);
            $stats['total_businesses'] = $stmt->fetch(PDO::FETCH_ASSOC)['total'];

            // Businesses by type
            $query = "SELECT business_type, COUNT(*) as count 
                     FROM businesses 
                     GROUP BY business_type";
            $stmt = $this->conn->query($query);
            $stats['by_type'] = $stmt->fetchAll(PDO::FETCH_ASSOC);

            // Businesses by year
            $query = "SELECT YEAR(registration_date) as year, COUNT(*) as count 
                     FROM businesses 
                     GROUP BY YEAR(registration_date)
                     ORDER BY year";
            $stmt = $this->conn->query($query);
            $stats['by_year'] = $stmt->fetchAll(PDO::FETCH_ASSOC);

            // Businesses by barangay
            $query = "SELECT barangay, COUNT(*) as count 
                     FROM businesses 
                     GROUP BY barangay";
            $stmt = $this->conn->query($query);
            $stats['by_barangay'] = $stmt->fetchAll(PDO::FETCH_ASSOC);

            return $this->formatResponse(true, $stats);
        } catch (PDOException $e) {
            return $this->formatResponse(false, null, $e->getMessage());
        }
    }

    private function formatResponse($success, $data, $error = null) {
        return json_encode([
            'success' => $success,
            'data' => $data,
            'error' => $error
        ]);
    }
}

// Handle the request
$api = new BusinessAPI();

// Get the request method and parameters
$method = $_SERVER['REQUEST_METHOD'];
$request = isset($_SERVER['PATH_INFO']) ? explode('/', trim($_SERVER['PATH_INFO'], '/')) : [];
$endpoint = $request[0] ?? '';

switch ($method) {
    case 'GET':
        if (isset($request[1])) {
            // Get specific business
            echo $api->getBusinessById($request[1]);
        } else {
            // Get all businesses or filtered by type
            $type = $_GET['type'] ?? null;
            echo $api->getBusinesses($type);
        }
        break;
        
    default:
        http_response_code(405);
        echo json_encode(['error' => 'Method not allowed']);
        break;
} 