<?php
header('Content-Type: application/json');

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $to = "info.hopetechservices@gmail.com"; 

    // Honeypot check
    if (!empty($_POST["website_url"])) {
        echo json_encode(["status" => "error", "message" => "Spam detected."]);
        exit;
    }

    $name    = filter_var(trim($_POST["name"] ?? ''), FILTER_SANITIZE_STRING);
    $email   = filter_var(trim($_POST["email"] ?? ''), FILTER_SANITIZE_EMAIL);
    $phone   = filter_var(trim($_POST["phone"] ?? ''), FILTER_SANITIZE_STRING);
    $message = filter_var(trim($_POST["message"] ?? ''), FILTER_SANITIZE_STRING);

    if (empty($name) || empty($message) || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
        echo json_encode(["status" => "error", "message" => "Please fill all fields correctly."]);
        exit;
    }

    $subject = "New Solar Quote: $name";
    $email_content = "Name: $name\nEmail: $email\nPhone: $phone\n\nDetails:\n$message";
    $headers = "From: HOPETECH Website <noreply@hopetechservices.com>";

    // Attempt to send
    if (mail($to, $subject, $email_content, $headers)) {
        echo json_encode(["status" => "success"]);
    } else {
        echo json_encode(["status" => "error", "message" => "Server failed to send email."]);
    }
} else {
    echo json_encode(["status" => "error", "message" => "Invalid request method."]);
}
?>