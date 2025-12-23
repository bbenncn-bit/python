package test;
import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;
import com.runyi.ryplat.api.commons.Result;
import com.ry.server.exgateway.commons.utils.HttpClientUtils;
import com.ry.server.exgateway.commons.utils.JacksonUtils;
import com.ry.server.exgateway.openapi.dto.TokenVO;

import java.util.HashMap;
import java.util.Map;

/**
 * @FileName: TestPro
 * @Author: 李曜呈
 * @Date: 2025/3/13 13:39
 * @Description:
 */
public class TestPxDp {
    public static void main(String[] args) {
        Result<String> result = new Result<>();
        //token地址
        String apiUrl = "https://www.oylianjin.com/ecopenapi/open/n/token/gen";
        //请求的接口地址
        String erpInterfaceUrl = "https://www.oylianjin.com/ecopenapi/a/trade/receipt/query/changzhi/receipt";// 替换成对应的接口
	//https://www.oylianjin.com/ecopenapi/operator/a/queryChangZhiBoseInfo
	//https://www.oylianjin.com/ecopenapi/basic/a/trade/receipt/query/changzhi/totalInfo
        String appId = "CZDP";
        String accessKey = "5fe632cf1ed54eb884129b7ffbd3521";
        String privateKey = "MIICeAIBADANBgkqhkiG9w0BAQEFAASCAmIwggJeAgEAAoGBAMjIidy6/qvBd9EVyNbKabbnESlbatQw9lHLzjHWFKDfl7E24fuj0m8xurZEVzhUYal9af7sMlYPcEma13i4xJ6faGOvJHseYlkoJRVHcJOq02tFDd3U2rZ98X3OjHC7CIFbIGM27GTvh41nsrexOJi0S3l3V0JWH/ooMeZiaWEXAgMBAAECgYEApiR7H7GEhu+Ci/sww7uemoC9zLEexxL04F568vYo/63FQhkeCjJXMTe/Po9ydOQuJCfpC867IEeKLP36CqUp3HhEBMnaOUFLMrF95BkFNu/QS1TmVe3xfoo66962VEimmV0Rrc+YeK3nTvLFUzCCgCKM/xArQFZMiWJ435MzASECQQDwdC5N77nHyTj2xiUcwUQHpZHIO9rMu0B3svkOwUbfqhOMHd5lR3URbE0/G0pq/RJrlH3gR5Fz0NySB/cT6yE/AkEA1cPCqNKgfCTY3skKg1UGQUlFYt4tf0sWPA1zqYe4RhkmGpA6ZZZvE9Y2SFnEIBdch6BE1uH+KbWQdCe3Q01yKQJBAISl8y13hCuc7FnmsW6Nh7QYOLYXnvq2ijf+ebsUEL8umh4AFEIXC5QTBQI9Ue53sgO7JT3m/WzA2g2Na1aHrg0CQQDSXa9Akt9qrJxcSr601kSslR3amUlu/wbnnFlZ2f2HxpIQDCXb+XpgrCuJcgWnizX9JsT4Lzj/9PUuyjL44ctZAkAEyQTmtZI46y8fwuOiiAQ9orPDQmc8jzHNRpQqQ3Ghc8KlAhQj/sEPixFW6TMrxwfFy2CGEplwVtvNubu9zfMO";
        TokenVO tokenVO = new TokenVO();
        tokenVO.setAppId(appId);
        tokenVO.setAccessKey(accessKey);
        String json = JacksonUtils.toJSon(tokenVO);
        Map<String, Object> map = new HashMap();
        map.put("appId", tokenVO.getAppId());
        map.put("accessKey", tokenVO.getAccessKey());
        Map<String, Object> headers = new HashMap<>();
        headers.put("appId", appId);
        headers.put("timestamp",  System.currentTimeMillis() + "");
        try {
            headers.put("signVal", EncryptData.encrptDataForObject(map, privateKey));
            String excuteResult = HttpClientUtils.httpPostJson(apiUrl, json, headers);
            result = JacksonUtils.readValue(excuteResult, Result.class);
            System.out.println(JSON.toJSONString(result));
            String token = result.getData();//获取token
            Map<String, Object> param = new HashMap();
            String jsonParam ="{\"startDate\": \"2025-05-27\",\"endDate\": \"2025-05-27\"}";
            param = JacksonUtils.readValue(jsonParam, Map.class);
//            //封装请求头
            Map<String, Object> header = getHeader(param,token,appId,privateKey);
            System.out.println(header);
            //请求erp的入参
            String jsonStr = JacksonUtils.toJSon(param);


            System.out.println("调用ec接口：*******************************" +erpInterfaceUrl );
            System.out.println("调用ec接口入参json：***********************" + jsonStr);
            long l = System.currentTimeMillis();
            String resultData = HttpClientUtils.httpPostJson(erpInterfaceUrl, jsonStr, header);
            System.out.println(System.currentTimeMillis()-l);
            System.out.println("调用ec接口返回原始数据******************" + resultData);

            System.out.println(JSONObject.parseObject(resultData));
        } catch (Exception e) {
            result.setSuccess(false);
            result.setMessage("获取token'错误:" + e.getMessage());
        }
    }

    /**
     * 获取请求头
     * 公共4个参数
     * @param map
     * @return
     */
    private static Map<String, Object> getHeader(Map map, String token,String appId,String privateKey) {


        //处理遇到Date的数据签名验证不通过的问题

        Map<String, Object> header = new HashMap<String, Object>();

        header.put("appId", appId);
        header.put("token", token);
        header.put("Authorization", token);
        header.put("signVal", EncryptData.encrptDataForObject(map, privateKey));//生成签名
        header.put("timestamp", System.currentTimeMillis() + "");// 时间戳


        return header;

    }
}

