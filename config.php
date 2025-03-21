<?php
$host = 'localhost';
$user = 'root';
$pass = 'Filda942703';
$db   = 'autobazar';

$conn = new mysqli($host, $user, $pass, $db);

if($conn->connect_error) {
    die("Připojení selhalo: " . $conn->connect_error);
}

echo "Připojení k databázi bylo úspěšné!";
?>
