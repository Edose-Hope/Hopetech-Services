<?php
// ----------------------------------------------------
// 1. CONFIGURATION: REPLACE THESE WITH YOUR OWN DETAILS
// ----------------------------------------------------

// The email address where you want to receive the quote requests
$receiving_email_address = 'YOUR_BUSINESS_EMAIL@EXAMPLE.COM'; 

// Subject for the email you receive
$subject = "New Solar Quote Request from Website"; 

// Your company name
$company_name = "HOPETECH SERVICES"; 

// ----------------------------------------------------
// 2. INPUT SANITIZATION
// ----------------------------------------------------

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    // Collect and sanitize input data
    $name = strip_tags(trim($_POST["name"]));
    $email = filter_var(trim($_POST["email"]), FILTER_SANITIZE_EMAIL);
    $phone = strip_tags(trim($_POST["phone"]));
    $message = trim($_POST["message"]);

    // Check that data was sent and is valid
    if (empty($name) OR empty($message) OR empty($phone) OR !filter_var($email, FILTER_VALIDATE_EMAIL)) {
        http_response_code(400); // Bad Request
        echo "Oops! There was a problem with your submission. Please complete the form and try again.";
        exit;
    }

    // ----------------------------------------------------
    // 3. EMAIL CONTENT CONSTRUCTION
    // ----------------------------------------------------
    
    // Build the email content
    $email_content = "Quote Request for " . $company_name . "\n\n";
    $email_content .= "Name: " . $name . "\n";
    $email_content .= "Email: " . $email . "\n";
    $email_content .= "Phone: " . $phone . "\n\n";
    $email_content .= "Project Details:\n" . $message . "\n";

    // Build the email headers (ensures proper sending and reply-to)
    $email_headers = "From: " . $company_name . " <noreply@yourdomain.com>\r\n";
    $email_headers .= "Reply-To: " . $name . " <" . $email . ">\r\n";
    $email_headers .= "MIME-Version: 1.0\r\n";
    $email_headers .= "Content-Type: text/plain; charset=UTF-8\r\n";

    // ----------------------------------------------------
    // 4. SEND EMAIL
    // ----------------------------------------------------
    
    // Use PHP's built-in mail() function
    if (mail($receiving_email_address, $subject, $email_content, $email_headers)) {
        http_response_code(200);
        echo "SUCCESS"; // Success message for JavaScript
    } else {
        http_response_code(500); // Internal Server Error
        echo "Oops! Something went wrong and we couldn't send your message.";
    }

} else {
    http_response_code(403); // Forbidden
    echo "There was a problem accessing this page.";
}
?>