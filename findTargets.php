<?
function minutesToStr($minutes)
{
    if ($minutes < 60)
        return sprintf("%dm", $minutes);
    else if ($minutes < 1440)
        return sprintf("%dh %dm",
            floor($minutes / 60),
            $minutes % 60
        );
    else
        return sprintf("%dd %dh %dm", 
            floor($minutes / 1440),
            floor(($minutes % 1440) / 60),
            ($minutes % 1440) % 60
        );
}
?>
<html>
<head>
<style>
table {border-collapse: collapse;}
td {padding-left: 1em; padding-right: 1em; text-align: center;}

</style>
</head>
<body>

<h1>P&amp;W targets finder</h1>

<p>The cached list of nations was last updated
<?
$cacheAge = (time() - filemtime("nations.txt")) / 60;

$cacheAgeStr = minutesToStr($cacheAge);

echo($cacheAgeStr);
?>
 ago.</p>

<?php
if (isset($_REQUEST["apiKey"]))
    $apiKey = $_REQUEST["apiKey"];
else
    $apiKey = "";

if (isset($_REQUEST["myNationId"]))
    $myNationId = $_REQUEST["myNationId"];
else
    $myNationId = 142203;


if (isset($_REQUEST["targetAlliances"]) && $_REQUEST["targetAlliances"] != "")
    $targetAlliances = explode(",", $_REQUEST["targetAlliances"]);
else
    $targetAlliances = array("None");

$apiUrl = sprintf("http://politicsandwar.com/api/nation/id=%d/&key=%s", $myNationId, $apiKey);
// var_dump($apiUrl);
$f = fopen($apiUrl, "r");
$myNation = json_decode(fgets($f), TRUE);
//var_dump($myNation);
if ($myNation["success"] == true)
{

    fclose($f);
    $scoreLow = $myNation["score"]*0.75;
    $scoreHigh = $myNation["score"]*1.75;
    /* var_dump($targetAlliances); */

    $f = fopen("nations.txt", "r");
    $json = fgets($f); 
    fclose($f);

    $targets = json_decode($json, TRUE)["nations"];
    $targets = array_filter( $targets,
        function($n){
            global $targetAlliances;
            return in_array($n["alliance"], $targetAlliances);
        } 
    );

    $targets = array_map( 
        function($n){
            $n["score"] = (float)($n["score"]);
            return $n;
        }, $targets);

    $targets = array_filter( $targets, 
        function($n){
            global $scoreHigh, $scoreLow;
            return $n["score"] >= $scoreLow 
                && $n["score"] <= $scoreHigh
                && $n["vacmode"] == 0
                ; } );
?>
<p>Here are the nations that <a href="<?printf("https://politicsandwar.com/nation/id=%d", $myNationId)?>">
<?=$myNation["name"]?></a> 
(score: <?=$myNation["score"]?>, alliance: <?=$myNation["alliance"]?>) could attack, 
from the following alliances:
<ul>
<? 
    foreach ($targetAlliances as $alliance)
    {
        printf("<li>%s</li>\n", $alliance);
    }
?>
</ul>
<!-- Nations that are either beiged or out of defensive slots are shown in grey. -->
</p>

<table style="margin-left: auto; margin-right: auto;">
<thead style="text-align: center; font-weight: 600;">
<tr>
<td>nation</td>
<td>alliance</td>
<td>colour</td>
<td>score</td>
<td>cities</td>
<td>offensive<br/>wars</td>
<td>defensive<br/>wars</td>
<td>inactive</td>
</tr>
</thead>

<tbody>
<?
// var_dump($targets);
    $rowCtr = 0;

    foreach ($targets as $id=>$n)
    {

        $inactivity = $n["minutessinceactive"] + $cacheAge;

        $isInactive = $inactivity > 20160;
        $isBeige = $n["color"] == "beige";
        $isFull = $n["defensivewars"] == 3;
    
        if ($isBeige || $isFull)
            // printf("<tr style=\"color: #AAAAAA;\">");
            continue;
        else
        {
            $rowCtr++;
            $rowCtr % 2 == 0 ? 
                printf("<tr style=\"background-color:peachpuff\">")
            :
                printf("<tr style=\"background-color:lavender\">")
            ;

?>
  <td style="text-align: right;">
  <a href="https://politicsandwar.com/nation/id=<?=$n["nationid"]?>"
     style="text-decoration: none; font-weight: bold;"
     target="_blank">
                  <?=$n["nation"]?>
  </a>
  </td>
  <td style="text-align: center;"><?=$n["alliance"]?></td>
  <td style="text-align: center;"><?=$n["color"]?></td>
  <td style="text-align: right;"><?=sprintf("%.2f", $n["score"])?></td>
  <td style="text-align: center;"><?=$n["cities"]?></td>
  <td><?=$n["offensivewars"]?></td>
  <td><?=$n["defensivewars"]?></td>
  <td style="text-align: right;">
  <?=minutesToStr($inactivity)?></td>
</tr>
<?
        }
    }
?>
</tbody>
</table>
<? 
} 
else
{
    if ($_SERVER["REQUEST_METHOD"] == "POST")
    {
?>
<p>(No nation specified or JSON request failed. Try checking your API key?)</p>
<?
    }
}
?>

<h2>New search</h2>

<form action="<?=$_SERVER["PHP_SELF"]?>" method="post">
Nation ID: <input type="text" name="myNationId" value="<?=$myNationId?>"/><br/>
Target alliances (comma separated without spaces): <br/>
        <input type="text" name="targetAlliances" 
               value="<?=isset($targetAlliances) ? implode(",", $targetAlliances) : ""?>"
               style="width: 600px"/><br/>
API key: <input type="text" name="apiKey" value="<?=$apiKey?>"/><br/>
<input type="submit" value="Search"/>
</form>

<p>You can find your API key on your <a
href="https://politicsandwar.com/account/#7" target="_blank">Account
Settings</a> page.</p>

<h2>Update the list of nations</h2>

<form action="updateNations.php" method="post">
API key: <input type="text" name="apiKey"/><br/>
<input type="submit" value="Update nations"/>
</form>


</body>
</html>
