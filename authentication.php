<?php

// init_set('display_errors', 1);
// error_reporting(E_ALL);

require 'connection.php';

// echo "string";
// die();

$uname = mysqli_real_escape_string($conn,$_POST['useremailid']);
$password = mysqli_real_escape_string($conn,$_POST['userpass']);

 if ($uname != "" && $password != ""){

   $sql_query = $conn->query("SELECT * FROM login WHERE emailaddress ='".$uname."' AND password = '".$password."'");

   if($sql_query->num_rows > 0){
         session_start();

        $_SESSION['uname'] = $uname;
        header('Location: home.php');
   }
   else{
            echo "Invalid username and password";
    }


    }

?>
