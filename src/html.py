index = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
  <head>
    <style type="text/css">
      form { display: table; }
      p { display: table-row; }
      label { display: table-cell; text-align: right; }
      input { display: table-cell; margin-left: 10px; }
      input[readonly] { background-color: #E0E0E0; }
    </style>
  </head>
  <body>
    Yubico Yubikeys:<br />
    <form action="/wsapi/2.0/verify" method="GET">
      <p><label for="otp">OTP</label><input type="text" name="otp" id="otp" /></p>
      <p><label for="id">API id</label><input type="text" name="id" id="id" value="1" /></p>
      <p><label for="nonce">Nonce</label><input type="text" name="nonce" id="nonce1" readonly /></p>
      <p><input type="submit" /></p>
    </form>
    <br />

    <!--OATH/HOTP tokens:<br />
    <form action="/wsapi/2.0/oathverify" method="GET">
        <p><label for="otp">OTP</label><input type="text" name="otp" id="otp" /></p>
        <p><label for="id">Public id</label><input type="text" name="publicid" id="id" /></p>
        <p><label for="id">API id</label><input type="text" name="id" id="id" value="1" /></p>
        <p><label for="nonce">Nonce</label><input type="text" name="nonce" id="nonce2" readonly /></p>
        <p><input type="submit" /></p>
    </form>-->

    <script>
      function gen_nonce(length) {
      var text = '';
      var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
      for (var i=0; i < length; i++)
            text += possible.charAt(Math.floor(Math.random() * possible.length));
            return text;
      }
      document.getElementById('nonce1').value = gen_nonce(16);
      //document.getElementById('nonce2').value = gen_nonce(16);
    </script>
  </body>
</html>
'''
