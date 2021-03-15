<?php
include "connection.php";

// Check user login or not
if(!isset($_SESSION['uname'])){
    header('Location: dashboard.php');
}

// logout
if(isset($_POST['but_logout'])){
    session_destroy();
    header('Location: login.php');
}
?>