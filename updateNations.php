<?php
/* Update the list of nations */

$executionStartTime = microtime(true);

if (isset($_REQUEST["apiKey"]))
    $apiKey = $_REQUEST["apiKey"];
else
    die("Please give your API key to update the list of nations.");

$apiUrl = sprintf("http://politicsandwar.com/api/nations/?key=%s", $apiKey);

flush();
echo("Updating nation list...");

$f = fopen($apiUrl, "r") or die(sprintf("Sorry, couldn't open %s", $apiUrl));
$apiRes = fgets($f);
fclose($f);

$nationsJson = json_decode($apiRes, TRUE);
if ($nationsJson["success"] == false)
    die("API request failed.");
else
{
    $g = fopen("nations.txt", "w");
    fputs($g, $apiRes);
    fclose($g);

    $executionEndTime = microtime(true);
    $seconds = $executionEndTime - $executionStartTime;
?>
Nation list updated successfully (<?=$seconds?>s)
<a href="findTargets.php">back</a>
<?
}

?>
