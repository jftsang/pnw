<?php
if (isset($_REQUEST["myNationId"]))
    $myNationId = $_REQUEST["myNationId"];
else
    $myNationId = 142203;

$f = fopen( sprintf("http://politicsandwar.com/api/nation/id=%d", $myNationId), "r");
$myNation = json_decode(fgets($f), TRUE);
fclose($f);
$scoreLow = $myNation["score"]*0.75;
$scoreHigh = $myNation["score"]*1.75;


$f = fopen("nations.txt", "r");
$json = fgets($f); 
fclose($f);

$raidables = json_decode($json, TRUE)["nations"];
$raidables = array_filter( $raidables,
    function($n){
        return $n["allianceid"] == 0 && $n["color"] != "beige";} );

$raidables = array_map( 
    function($n){
        $n["score"] = (float)($n["score"]);
        return $n;
    }, $raidables);

$raidables = array_filter( $raidables, 
    function($n){
        global $scoreHigh, $scoreLow;
        return $n["score"] >= $scoreLow 
            && $n["score"] <= $scoreHigh
            && $n["defensivewars"] < 3
            && $n["vacmode"] == 0
     ; } );
?>
<html>
<body>

<table style="margin-left: auto; margin-right: auto;">
<thead style="text-align: center; font-weight: 600;">
<tr>
<td style="width: 225px;">nation</td>
<td style="width: 50px;">score</td>
<td style="width: 100px;">inactive</td>
</tr>
</thead>

<tbody>
<?
foreach ($raidables as $id=>$n)
{
    $isInactive = $n["minutessinceactive"] > 20160;

    if ($isInactive)
        printf("<tr style=\"color: gray; font-style: italic\">");
    else
        printf("<tr>");
?>
  <td style="text-align: center;">
  <a href="https://politicsandwar.com/nation/id=<?=$n["nationid"]?>"
     style="text-decoration: none; font-weight: bold; color: black;">
                  <?=$n["nation"]?>
  </a>
  </td>
  <td style="text-align: right;"><?=$n["score"]?></td>
  <td style="text-align: right;">
  <?=sprintf("%dd %dh %dm", 
    floor($n["minutessinceactive"] / 1440),
    floor(($n["minutessinceactive"] % 1440) / 60),
    ($n["minutessinceactive"] % 1440) % 60
  )
  ?></td>
</tr>
<?
}
?>
</tbody>
</table>

</body>
</html>
