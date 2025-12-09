<?php
header("Content-Type: application/json");

if (!isset($_GET['file'])) {
    echo json_encode(["error" => "No file specified"]);
    exit;
}

$allowed = ["commands.json", "clients.json"];
$file = $_GET['file'];

if (!in_array($file, $allowed)) {
    echo json_encode(["error" => "Access denied"]);
    exit;
}

$data = file_get_contents("php://input");

if ($data === false) {
    echo json_encode(["error" => "No data received"]);
    exit;
}

// Validate JSON
$json = json_decode($data, true);
if ($json === null && json_last_error() !== JSON_ERROR_NONE) {
    echo json_encode(["error" => "Invalid JSON"]);
    exit;
}

// Use LOCK_EX to avoid race conditions
$result = file_put_contents($file, json_encode($json, JSON_PRETTY_PRINT), LOCK_EX);

if ($result === false) {
    echo json_encode(["error" => "Failed to write file"]);
} else {
    echo json_encode(["success" => true]);
}
?>
