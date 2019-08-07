<?php
$f = fopen("http://politicsandwar.com/api/nation/id=142203", "r");
$json = fgets($f);
fclose($f);
$json = json_decode($json, TRUE);
?>
<pre>
<?php
var_dump(($json));
?>
</pre>
