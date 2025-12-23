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
        String erpInterfaceUrl = "https://www.oylianjin.com/ecopenapi/basic/a/trade/receipt/query/pingxiang/receipt";// 替换成对应的接口
        String appId = "PXDP";
        String accessKey = "226b673950704a5c971b236f88948fe1";
        String privateKey = "MIICdQIBADANBgkqhkiG9w0BAQEFAASCAl8wggJbAgEAAoGBAICbt0M96LyKMP4bdFMIql+7gbOmXw/K+13qg3IsBdlsEoW7B3yFa9Bffhv1TIOZ7plTAxHy4hV0XbNTotJccmlVk2rq4V3lMCP5O3sbHmNOuewUFrV7A1pewEQIVmETxstrGi2YCcTzjkquI6e7x/CcDuSC+V+rK97EUcNWavz1AgMBAAECgYAnFKqE4Ww21tt6bEdV8B0tyCHqwJTEjM8Dw/67lAsW/dNHFgV5XmXbxRjiUBE3MHCj4Oje7GqtUFYk5zZkLDmLv+uIzCl7f7hnX6eZUA19nY/cSqowZ87K1ZavIIS2wcr6p73MNgTfefFuIpqjnYs4t1Uap5Tj92sD2Icvn9h14QJBAMgC23APecJDw8XS1P4P2KavEHqORaOTm7s8vc2lpxMIqpkIBU15s/YqNURKjMEVR+O+tP5QJy2ba/AWzASKaT0CQQCknAE1Zrn4eoVmwCNPKqv84HpcTNeG7OboStA3yYhQMA2UryobKqmkFALZ1yyjorP/zNZPpDncqb46MV/kUO4ZAkAQ0myyWBrdg+WLVdgkJiEKo9628BBbWabXcJxmF3Cd4TS3+jy372x7X8FrJPoBo1CQjxGZ8hPZeiDx6HjwSNPhAkA+MoA2aFFetRTQ5UqyMCJ6U2uIkrRhVARPw2z3l1u9SNro0mLrjuw4hiMpoqdIUUMIJaLYxuniGfU50cw03euJAkAzk844q1N8WP2H9fVtC7M/FMBfqXZSFk+O96BVboSJNsTqao1slq6ArY47fh0Xfl7e30dSFj8zp/rD1REde8pB";
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

