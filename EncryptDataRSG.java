package test;

import java.util.Map;
import java.security.Signature;
import java.security.KeyFactory;
import java.security.PrivateKey;
import java.security.spec.PKCS8EncodedKeySpec;
import java.util.Base64;
import java.util.Collections;
import java.util.HashMap;

public class EncryptData{

        private static final String SIGN_ALGORITHMS = "SHA1WithRSA";
        public static String encrptDataForObject(Map<String, Object> map, String private_key) {
            HashMap<String, String> toMap = new HashMap<String, String>();
            for (Map.Entry<String, Object> entry : map.entrySet()) {
                String key = entry.getKey();
                Object value = entry.getValue();
                if (value == null) {
                    toMap.put(key, "null");
                }
                if (value instanceof String) {
                    toMap.put(key, (String)value);
                    continue;
                }
                if (value instanceof Boolean) {
                    toMap.put(key, value.toString());
                    continue;
                }
                if (value instanceof Byte) {
                    toMap.put(key, value.toString());
                    continue;
                }
                if (value instanceof Character) {
                    toMap.put(key, value.toString());
                    continue;
                }
                if (value instanceof Double) {
                    toMap.put(key, value.toString());
                    continue;
                }
                if (value instanceof Float) {
                    toMap.put(key, value.toString());
                    continue;
                }
                if (value instanceof Integer) {
                    toMap.put(key, value.toString());
                    continue;
                }
                if (value instanceof Long) {
                    toMap.put(key, value.toString());
                    continue;
                }
                if (!(value instanceof Short)) continue;
                toMap.put(key, value.toString());
            }
            if (toMap.isEmpty()) {
                toMap.put("sign_val", "sign_val");
            }
            String keyValueStr = createLinkString(toMap);
            String signVal = sign(keyValueStr, private_key, "utf-8");
            return signVal;
        }
        private static String createLinkString(Map<String, String> params) {
            java.util.List<String> keys = new java.util.ArrayList<String>(params.keySet());
            Collections.sort(keys);
            String prestr = "";
            for (int i = 0; i < keys.size(); ++i) {
                String key = (String)keys.get(i);
                String value = params.get(key);
                prestr = i == keys.size() - 1 ? prestr + key + "=" + value : prestr + key + "=" + value + "&";
            }
            return prestr;
        }
        private static String sign(String content, String privateKey, String input_charset) {
            try {
                PKCS8EncodedKeySpec priPKCS8 = new PKCS8EncodedKeySpec(Base64.getDecoder().decode((String)privateKey));
                KeyFactory keyf = KeyFactory.getInstance("RSA");
                PrivateKey priKey = keyf.generatePrivate(priPKCS8);
                Signature signature = Signature.getInstance(SIGN_ALGORITHMS);
            signature.initSign(priKey);
            signature.update(content.getBytes(input_charset));
            byte[] signed = signature.sign();
            String sign = Base64.getEncoder().encodeToString((byte[])signed);
            return sign;
        }
        catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }

}
