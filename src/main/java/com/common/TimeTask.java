package com.common;

import com.alibaba.fastjson.JSON;
import com.controller.CookieController;
import com.entity.Course;
import com.entity.StudyCookie;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.apache.http.Header;
import org.apache.http.HttpEntity;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.ContentType;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.util.EntityUtils;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.io.File;
import java.io.IOException;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

@Component
@Slf4j
public class TimeTask {
    private static String[] zyk = "66526,66527,66528,66529,66530,66531,66532,66533,66534,66535,66536,66537,66538,66539,66540,66541,66542,66543,66544,66545,66546,66547,66548,64353,64352,64351,64350,64349,64348,64347,66821,66822,66823,66824,66825,66826,66827,66828,66829,66830,66831,66832,66840,66841,66842,66857,66858,66859,66860,66861,66862,66802,66803,66804,66805,66806,66807,66808,66809,66810,64346,64345,64344,64343,64342,64341,64340,64339,64338,64337,64336,64335,64334,64333,64286,64285,64284,64283,64282,64281,64280,64279,64278,64277,64276,64275,64274,64273,64272,64271,64270,64269,64268,64267,64266,64265,64264,64263,64262,64261,64260,64259,64332,64331,64330,64329,64328,64327,64326,64325,64324,64323,64322,64321,64320,64319,64318,64317,64316,64315,66811,66812,66813,66814,66815,66816,66817,66818,66819,66820,66833,66834,66835,66836,66837,66838,66839,66851,66852,66853,66854,66855,66856,66519,66520,66521,66522,66523,66524,66525,53575,53574,53573,53572,53571,53570,53569,53568,53567,53566,53565,53564,53563,53562,53561,53560,53557,53556,53555,53554,53553,53552,53551,53550,53549,53548,53547,53546,53545,53544,53527,53526,53525,53086,53085,53084,53083,53082,53081,53080,53061,53060,53059,53058,53057,53056,53055,53054,53053,53052,53051,53050,53049,53048,53079,53078,53077,53076,53075,53074,64314,64313,64312,64311,64310,64309,64308,64307,64306,64305,64304,64303,64302,64301,64300,64299,64298,64297,64296,64295,64294,64293,64292,64291,64290,64289,64288,64287,64258,64257,53543,53542,53541,53540,53539,53538,53537,53536,53535,53534,53533,53532,53531,53589,53588,53587,53586,53585,53584,53583,53582,53581,53580,53579,53578,53577,53576,53530,53529,53528,53073,53072,53071,53070,53069,53068,53067,53066,53065,53064,53063,53062,53025,53024,53023,53022,53021,53020,53019,53018,53017,53016,53015,53014,53047,53046,53045,53044,53043,53042,53041,53040,53039,53038,53037,53036,53034,53033,53032,53031,53030,53029,53028,53027,53026,39323,39250,39251,39848,39847,39846,39845,39844,39843,39842,39841,39840,39839,39838,39837,39265,39264,39263,39262,39261,39260,39259,39258,39257,39256,39255,39254,39253,39252,39237,39249,39248,39247,39246,39245,39244,39243,39242,39241,39240,39239,39238,39236,39319,39318,39324,39322,39321,39320,39343,39342,39341,39340,39339,39338,39337,39336,39335,39334,39333,39332,39331,39329,39328,39327,39326,39325,39273,39272,39271,39836,39270,39835,39834,39269,39833,39832,39268,39831,39267,39830,39266,39829,39828,39827,39826,39825,39824,39823,39822,39821,39820,39819,39818,39817,39816,39852,39851,39850,39849,39815,39814,39813,39812,39330,39317,39316,39315,39314,39313,39312,39311,39310,39309,39308,39307,39306,39305,39304,39303,39302,39301,39300,39299,39298,39297,39296,39295,39294,39293,39292,39291,39290,39289,39288,39287,39286,39285,39284,39283,39282,39281,39280,39279,39278,39277,39276,39275,39274,37917".split(",");
    private static String[] hygx = "67015,67373,67045,66984,67374,66985,67016,67046,66986,67375,67017,66987,67376,67047,67018,67377,66988,67019,67048,67378,66989,67020,67385,66990,67021,67049,67386,66991,67022,67050,67387,67023,67051,66993,67052,67388,67024,66994,67389,67053,66995,67025,67390,66996,67054,67026,67394,66997,67395,67055,67027,66998,67412,67056,67028,67396,66999,67413,67397,67029,67000,67414,67057,67415,67398,67001,67030,67058,67416,67399,67417,67002,67031,67059,67400,67418,67003,67401,67419,67032,67060,67004,67402,67420,67033,67062,67403,67005,67034,67421,67404,67006,67063,67035,67422,67405,67007,67064,67406,67423,67008,67036,67009,67424,67407,67065,67037,67010,67408,67066,67425,67038,67011,67067,67409,67012,67039,67379,67068,67013,67040,67410,67069,67014,67380,67041,67411,67070,67042,67381,67071,67043,67382,67072,67044,67383,67074,67076,67384,67184,67077,67185,67186,67187,67188,67189,67190,66980,66981,66983,67078,67079,67080,67082,67083,67084,67086,67087,67089,67090,67091,67092,67093,67094,67095,67096,67097,67098,67099,67100,67101,67102,67103,67104,67105,67106,67107,67108,67109,67110,67318,67319,67320,67321,67322,67323,67324,67112,67113,67114,67115,67116,67117,67118,67119,67152,67153,67154,67155,67156,67157,67158,67159,67160,67161,67162,67163,67164,67165,67166,67213,67214,67215,67216,67217,67218,67219,67220,67221,67222,67223,67224,67225,67226,67227,67228,67229,67230,67231,67232,67233,67234,67235,67236,67237,67238,67239,67240,67241,67242,67111,67289,67290,67291,67292,67293,67294,67295,67296,67297,67298,67299,67300,67301,67302,67303,67304,67305,67306,67307,67308,67309,67310,67311,67312,67313,67314,67315,67316,67317,67167,67168,67169,67170,67171,67172,67173,67179,67191,67192,67193,67194,67195,67196,67197,67198,67199,67200,67201,67202,67203,67204,67205,67206,67207,67208,67209,67210,67211,67212,67243,67273,67244,67274,67245,67275,67246,67276,67247,67277,67248,67278,67249,67279,67250,67280,67251,67281,67282,67252,67283,67253,67284,67285,67254,67286,67255,67287,67256,67288,67257,67325,67258,67326,67259,67327,67260,67328,67261,67329,67262,67330,67263,67331,67264,67332,67265,67333,67266,67334,67267,67338,67268,67339,67269,67340,67270,67341,67271,67272,67342,67348,67349,67350,67351,67352,67353,67354,67355,67356,67357,67358,67359,67360,67361,67362,67363,67364,67365,67366,67367,67368,67369,67370,67371,67372,66927,66928,66929,66930,66931,66932,66933,66934,66935,66936,66937,66938,66939,66940,66941,66963,66964,66965,66966,66967,66968,66969,66970,66971,66972,66973,66974,66975,66976,66977,66978,66979,67120,67121,67122,67123,67124,67125,67126,67127,67128,67129,67130,67131,67132,67133,67134,67135,67136,67137,67138,67139,67140,67141,67142,67143,67144,67145,67146,67147,67148,67149,67150,67151,67174,67175,67176,67177,67178,67180,67181,67182,67183,67335,67336,67337,67343,67344,67345,67346,67347,66926,66307,66308,66309,66310,66311,66312,66313,66314,66315,66316,66317,66318,66349,66350,66351,66352,66353,66354,66355,66356,66357,66358,66359,66360,66361,66362,66363,66364,66365,66366,66367,66368,66369,66370,66371,66372,66373,66374,66375,66376,66377,66378,66319,66320,66321,66322,66323,66324,66325,66326,66327,66328,66329,66330,66331,66332,66333,66334,66335,66336,66337,66338,66339,66340,66341,66342,66343,66344,66345,66346,66347,66348,66379,66380,66381,66382,66383,66384,66385,66386,66387,66388,66389,66390,66391,66392,66393,66394,66395,66396,66397,66398,66399,66400,66401,66402,66403,66404,66405,66406,66407,66408,66409,66410,66411,66412,66413,66414,66415,66416,66417,66418,66419,66420,66421,66422,66423,66424,66425,66426,66427,66428,66429,66430,66431,66432,66433,66434,66435,66436,66437,66438,66111,66110,66141,66109,66140,66108,66139,66107,66138,66106,66137,66105,66136,66104,66135,66103,66134,66102,66133,66101,66132,66100,66131,66099,66130,66098,66129,66097,66128,66096,66127,66094,66126,66125,66095,66124,66093,66123,66092,66122,66091,66090,66121,66089,66120,66088,66119,66087,66086,66118,66117,66085,66116,66084,66115,66114,66082,66113,66083,66112,66081,66080,66079,66078,66077,66076,66075,66074,66072,66073,66070,66071,66069,66068,66067,66066,66064,66065,66063,66062,66061,66060,66059,66058,66057,66056,66055,66054,66053,66052,66051,66050,66049,66047,66048,66046,66045,66044,66043,66042,66041,66039,66040,66038,66037,66036,66035,66034,66033,66032,66031,66030,66029,66028,66027,66026,66025,66024,66023,66022,66439,66440,66441,66442,66443,66444,66445,66446,66447,66448,66449,66450,66451,66452,66306,66156,66155,66154,66153,66152,66151,66150,66149,66148,66147,66146,66145,66144,66143,66142,66021,66020,66019,66018,66017,66016,66015,66014,66012,66013,66011,66010,66009,66008,61299,61298,61297,61296,61294,61295,61293,61292,61291,61289,61290,61288,61287,61286,61284,61285,61283,61252,61282,61253,61280,61251,61250,61281,61248,61249,61279,61247,61278,61245,61246,61277,61244,61275,61243,61276,61274,61242,61273,61240,61271,61241,61272,61270,61239,61269,61238,61267,61268,61237,61266,61236,61265,61235,61263,61264,61233,61262,61234,61261,61259,61232,61260,61231,61258,61256,61230,61257,61255,61229,61254,61227,61228,61226,61225,61224,61223,61222,61220,61221,61219,61218,61217,61216,61215,61214,61213,61212,61211,61210,61209,61208,61207,61206,61205,61204,61202,61203,61201,61200,61199,61198,61197,61196,61195,61194,61193,61192,61191,61190,61189,61187,61188,61186,61185,61184,61183,61182,61180,61181,61179,61178,61177,61176,61175,61173,61174,61172,61171,61170,61169,61168,61167,61165,61166,61164".split(",");
    private static String[] ybgx = "64477,64447,64478,64448,64479,64449,64480,64450,64451,64481,64452,64482,64453,64483,64454,64484,64485,64455,64486,64456,64457,64487,64458,64488,64459,64489,64490,64460,64491,64461,64492,64493,64462,64494,64463,64495,64464,64496,64465,64497,64466,64498,64467,64499,64468,64500,64469,64501,64502,64470,64503,64471,64504,64472,64505,64473,64506,64474,64475,64476,64507,64508,64509,64510,64511,64512,64513,64514,64515,64516,64517,64518,64519,64520,64521,64522,64523,64524,64525,64526,64527,64528,64529,64530,64531,64532,64533,64534,64535,64536,64537,64538,64539,64540,64541,64542,64543,64544,64545,64546,64942,64943,64944,64945,64946,64947,64948,64949,64950,64951,64952,64953,64954,64955,64956,64957,64958,64959,64960,64961,64962,64963,64964,64965,64966,64967,64968,64969,64970,64971,64972,64973,64974,64975,64976,64977,64978,64979,64980,65116,65117,65118,65119,65120,65121,65122,65123,65124,65125,65126,65869,65870,65871,65872,65873,65874,64621,64622,64623,64624,64625,64626,64627,64628,64629,64630,64631,64632,64633,64634,64635,64636,64637,64638,64639,64640,64641,64642,64643,65514,65515,65516,65550,65551,65552,65553,65557,65558,65559,65564,65565,65566,65567,65857,65858,65859,65860,65861,65862,65863,65864,64591,64592,64593,64594,64837,64838,64839,64840,64841,64842,65070,65071,65072,65073,64575,64576,64577,64578,64581,64582,64583,64584,64585,64586,64587,64588,64589,64590,64831,64832,64833,64834,64835,64836,65066,65067,65068,65069,64553,64572,64573,64574,64579,64580,64601,64602,64603,64604,64605,64606,64607,64608,64609,64610,64611,64612,64613,64614,64615,64616,64617,64618,64619,64620,64644,64645,64646,64647,64648,64554,64595,64596,64597,64598,64599,64600,64547,64548,64549,64550,64551,64552,64555,64556,64557,64558,64559,64560,64561,64562,64563,64564,64565,64566,64567,64568,64569,64570,64571,64649,64650,64651,64652,64653,64654,64655,64656,64657,64658,64659,64660,64661,64662,64663,64664,64665,64666,64667,64668,64669,64670,64671,64672,64673,64674,64675,64676,64677,64678,64798,64799,64800,64801,64802,64859,64860,64981,64982,64983,64984,64985,64986,64987,64988,64989,64990,64994,64995,64996,64997,64998,64999,65000,65001,65002,65003,65004,65005,65006,65007,65008,65009,65010,65011,65012,65013,65014,65015,65016,65017,65018,65019,65020,65021,65022,65023,65024,65025,65026,65027,65028,65029,65030,65031,65032,65033,65034,65035,65036,65075,65076,65077,65078,65079,65953,65954,65955,65956,64807,64808,64809,64810,64811,64812,64813,64814,64815,64816,64817,64818,64819,64820,64821,64822,64823,64824,64825,64826,64827,65037,65038,65039,65040,65041,65042,65043,65044,65045,65046,65047,65048,65049,65050,65051,65052,65053,65054,65055,65056,65057,65058,65059,65060,65061,65062,65063,65064,65065,65074,64828,64829,64830,64851,64852,64853,64854,64855,64856,64857,64858,64861,64862,64863,64864,64865,64866,64867,64868,64869,64870,64871,64872,64873,64874,64875,64876,65170,65171,65172,65173,65174,65175,65176,65177,65178,65179,65180,65181,65182,65183,65184,65185,65186,65187,65188,65189,65190,65191,65192,65193,65194,65195,65196,65197,65198,65199,65200,65201,65202,65203,65204,65205,65206,65207,65208,65209,65210,65211,65212,65213,65214,65215,65216,65217,65218,65219,65220,65221,65222,65223,65224,65225,65226,65227,65228,65229,65230,65231,65232,65263,65264,65265,65266,65267,65268,65269,65270,65271,65272,65273,65274,65275,65276,65277,65278,65279,65280,65281,65282,65283,65284,65285,65286,65287,65288,65289,65290,65291,65292,65233,65234,65235,65236,65237,65238,65239,65240,65241,65242,65243,65244,65245,65246,65247,65248,65249,65250,65251,65252,65253,65254,65255,65256,65257,65258,65259,65260,65261,65262,65293,65294,65295,65296,65297,65298,65299,65300,65301,65302,65303,65304,65305,65306,65307,65308,65309,65310,65311,65312,65986,65987,65988,65989,65990,65991,65992,65993,65994,65995,65996,65997,65998,65999,66000,66001,66002,66003,66004,66005,66006,66007,64797,65127,65128,65387,65388,65389,65390,65391,65392,65393,65394,65395,65396,65397,65398,65399,65400,65401,65664,65665,65694,65695,65696,65697,65698,65699,65700,65701,65702,65703,65704,65705,65706,65707,65708,65709,65710,65711,65712,65713,65714,65715,65716,65717,65718,65719,65720,65721,65722,65723,65724,65725,65726,65727,65728,65729,65730,65731,65732,65733,65734,65735,65736,65737,65738,65739,65740,65741,65742,65743,65744,65745,65746,65747,65748,65749,65750,65751,65752,65753,65754,65755,65756,65757,65758,65759,65760,65100,65101,65102,65103,65104,65383,65384,65385,65386,65419,65420,65421,65422,65427,65428,65429,65430,65431,65432,65433,65434,65459,65460,65461,65462,65477,65478,65479,65577,65578,65579,65580,65584,65585,65586,65587,64778,64779,64780,64781,64782,64783,64784,64785,64786,64787,64792,64793,64794,64795,64796,65368,65369,65370,65371,65376,65377,65378,65379,65423,65424,65425,65426,65438,65439,65440,65441,65442,65443,65455,65456,65457,65458,65463,65464,65465,65466,65475,65476,65480,65481,65482,65483,65488,65489,65490,65491,65499,65500,65501,65517,65518,65519,65520,65521,65522,65523,65524,65538,65539,65540,65541,65554,65555,65556,65568,65569,65570,65581,65582,65583,65634,65635,65636,65637,65638,65639,65640,65641,65642,65643,65644,65645,65946,65947,65948,65364,65365,65366,65367,65380,65381,65382,65467,65468,65469,65470,65471,65472,65473,65474,65484,65485,65486,65487,65496,65497,65498,65502,65503,65504,65505,65529,65530,65531,65532,64752,64753,64754,64755,64756,64757,64758,64759,64760,64761,64762,64763,64764,64765,64766".split(",");
    private static Map<Integer, String[]> courseIds = new ConcurrentHashMap<>();
    private static Map<String, Map<Integer, Integer>> index;
    private static Map<String, Integer> error = new HashMap<>();

    static {
        courseIds.put(15, zyk);
        courseIds.put(16, hygx);
        courseIds.put(17, ybgx);
        index = FileUtil.read(new File("data"));
    }

    public static Map<String, Course> courses = new ConcurrentHashMap<>();

    /**
     * 心跳包
     *
     * @throws IOException
     */
    @Scheduled(cron = "0/30 * * * * ?")
    public void hearbeatTask() {
        for (Map.Entry<String, Course> entry : courses.entrySet()) {
            try {
                Course course = entry.getValue();
                String sign = update(entry.getKey(), course);
                for (StudyCookie cookie : CookieController.cookies.values()) {
                    if (cookie.getName().equals(entry.getKey())) {
                        cookie.setState("正常");
                        error.remove(entry.getKey());
                    }
                }
                if (sign != null) {
                    course.setSign(sign);
                    courses.put(entry.getKey(), course);
                } else {
                    courses.remove(entry.getKey());
                }
            } catch (Exception e) {
                log.error(entry.getKey() + "update异常----------------------", e);
                for (StudyCookie cookie : CookieController.cookies.values()) {
                    if (cookie.getName().equals(entry.getKey())) {
                        cookie.setState("异常");
                        if (!error.containsKey(entry.getKey())) {
                            error.put(entry.getKey(), 1);
                        } else {
                            error.put(entry.getKey(), error.get(entry.getKey()) + 1);
                        }
                    }
                }
                if (error.containsKey(entry.getKey()) && error.get(entry.getKey()) > 3) {
                    courses.remove(entry.getKey());
                }
            }
        }
    }

    @Scheduled(cron = "0 0/1 * * * ?")
    public void task() throws IOException {
        for (StudyCookie cookie : CookieController.cookies.values()) {
            try {
                if (courses.containsKey(cookie.getName())) {
                    continue;
                }
                if (StringUtils.isEmpty(cookie.getScore())) {
                    updateScore(cookie);
                }
                if (!index.containsKey(cookie.getName())) {
                    Map<Integer, Integer> m = new HashMap<>();
                    m.put(cookie.getType(), 0);
                    index.put(cookie.getName(), m);
                } else if (!index.get(cookie.getName()).containsKey(cookie.getType())) {
                    index.get(cookie.getName()).put(cookie.getType(), 0);
                }
                int courseIndex = index.get(cookie.getName()).get(cookie.getType());
                String courseId = courseIds.get(cookie.getType())[courseIndex];
                String logSign = start(cookie, courseId);
                cookie.setState("正常");
                String sign = logSign.split("#")[0];
                String logId = logSign.split("#")[1];
                courses.put(cookie.getName(), new Course(cookie.getType(), cookie.getValue(),
                        courseId, logId, sign));
            } catch (Exception e) {
                log.error(e.toString(), e);
                cookie.setState("异常");
            }
        }
    }

    @Scheduled(cron = "0 0 * * * ?")
    public void updateScore() throws IOException {
        for (StudyCookie cookie : CookieController.cookies.values()) {
            updateScore(cookie);
        }
    }

    private void updateScore(StudyCookie cookie) throws IOException {
        String response = sendPost(cookie.getName(), "https://learning.hzrs.hangzhou.gov.cn/api/index/Study.UserIndex/index",
                assertHeader(cookie.getValue()), JSON.toJSONString(new HashMap<>()));
        Map<String, Object> result = (Map<String, Object>) JSON.parse(response);
        int status = Integer.parseInt(result.get("status").toString());
        if (status == 200) {
            log.info("-----【{}】更新分数请求成功", cookie.getName());
            Map<String, Object> data = (Map<String, Object>) result.get("data");
            List<Map<String, Object>> study = (List<Map<String, Object>>) data.get("study");
            cookie.setScore(extractStudyScores(study));
        } else {
            log.error("----【{}】更新分数请求失败-------------------", cookie.getName());
            log.error(response);
        }
    }

    private String start(StudyCookie studyCookie, String courseId) throws IOException {
        Map<String, Object> start_course_session_body = new HashMap<>();
        start_course_session_body.put("courseId", courseId);
        start_course_session_body.put("delay", 1200);
        String response = sendPost(studyCookie.getName(), "https://learning.hzrs.hangzhou.gov.cn/api/index/Study.Index/startPlay",
                assertHeader(studyCookie.getValue()), JSON.toJSONString(start_course_session_body));
        Map<String, Object> result = (Map<String, Object>) JSON.parse(response);
        int status = Integer.parseInt(result.get("status").toString());
        if (status == 200 && result.containsKey("sign")) {
            log.info("--------------【{}】启动任务{}成功-------------------", studyCookie.getName(), courseId);
            Runnable task = () -> {
                try {
                    pause(studyCookie.getName(), courses.get(courseId));
                    Thread.sleep(3000);
                    confirm(studyCookie.getName(), courses.get(courseId));
                } catch (IOException | InterruptedException e) {
                    log.error("--------------【{}】暂停任务{}失败-------------------", studyCookie.getName(), courseId);
                    log.error(e.toString(), e);
                    throw new RuntimeException(e);
                }
            };
            DynamicTaskManager.scheduleTask(studyCookie.getName() + courseId, task);
            return result.get("sign") + "#" + result.get("logId");
        } else {
            log.error("--------------【{}】启动任务{}失败-------------------", studyCookie.getName(), courseId);
            log.error(response);
            throw new IOException();
        }

    }

    private void pause(String name, Course course) throws IOException {
        String response = sendPost(name, "https://learning.hzrs.hangzhou.gov.cn/api/index/Study.Index/autoPause",
                assertHeader(course.getCookie()), JSON.toJSONString(new HashMap<>()));
        Map<String, Object> result = (Map<String, Object>) JSON.parse(response);
        int status = Integer.parseInt(result.get("status").toString());
        if (status == 200) {
            log.info("-----【{}】更新暂停请求{}成功", name, course.getCourseId());
        } else {
            log.error("----【{}】更新暂停请求{}失败-------------------", name, course.getCourseId());
            log.error(response);
            throw new IOException();
        }
    }

    private void confirm(String name, Course course) throws IOException {
        String response = sendPost(name, "https://learning.hzrs.hangzhou.gov.cn/api/index/Study.Index/confirmPlay",
                assertHeader(course.getCookie()), JSON.toJSONString(new HashMap<>()));
        Map<String, Object> result = (Map<String, Object>) JSON.parse(response);
        int status = Integer.parseInt(result.get("status").toString());
        if (status == 200) {
            log.info("-----【{}】暂停反馈请求{}成功", name, course.getCourseId());
        } else {
            log.error("----【{}】暂停反馈请求{}失败-------------------", name, course.getCourseId());
            log.error(response);
            throw new IOException();
        }
    }

    private String update(String name, Course course) throws IOException {
        Map<String, Object> update_course_session_body = new HashMap<>();
        update_course_session_body.put("courseId", course.getCourseId());
        update_course_session_body.put("delay", 1200);
        update_course_session_body.put("logId", course.getLogId());
        update_course_session_body.put("sign", course.getSign());
        String response = sendPost(name, "https://learning.hzrs.hangzhou.gov.cn/api/index/Study.Index/updateStudy",
                assertHeader(course.getCookie()), JSON.toJSONString(update_course_session_body));
        Map<String, Object> result = (Map<String, Object>) JSON.parse(response);
        int status = Integer.parseInt(result.get("status").toString());
        if (status == 200 && result.containsKey("sign") && result.containsKey("data")) {
            Map<String, Object> data = (Map<String, Object>) result.get("data");
            int finish = Integer.parseInt(data.get("finish").toString());
            int playTime = Integer.parseInt(data.get("playTime").toString());
            if (finish == 0) {
                log.info("-----【{}】更新任务{}成功，time:【{}】------", name, course.getCourseId(), playTime);
                return result.get("sign").toString();
            } else {
                log.info(response);
                log.info("-------------【{}】任务{}結束，time:【{}】，继续下一个任务，------------------", name, course.getCourseId(), playTime);
                DynamicTaskManager.cancelTask(name + course.getCourseId());
                index.get(name).put(course.getType(), index.get(name).get(course.getType()) + 1);
                FileUtil.write(index, new File("data"));
                return null;
            }
        } else {
            log.error("--------------【{}】更新任务{}失败-------------------", name, course.getCourseId());
            log.error(response);
            throw new IOException();
        }
    }

    private Map<String, String> assertHeader(String cookie) {
        Map<String, String> headers = new HashMap<>();
        headers.put("Accept", "application/json, text/plain, */*");
        headers.put("Accept-Encoding", "gzip, deflate, br, zstd");
        headers.put("Accept-Language", "zh-CN,zh;q=0.9,en;q=0.8,sw;q=0.7");
//        headers.put("Authorization", authorization);
        headers.put("Connection", "keep-alive");
        headers.put("Content-Type", "application/json");
        headers.put("Cookie", cookie);
        headers.put("Host", "learning.hzrs.hangzhou.gov.cn");
        headers.put("Origin", "https://learning.hzrs.hangzhou.gov.cn");
        headers.put("Referer", "https://learning.hzrs.hangzhou.gov.cn/");
        headers.put("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36");
        return headers;
    }


    private Map<String, String> str2Map(String cookie) {
        Map<String, String> orderedMap = new LinkedHashMap<>();

        // 步骤1：按分号拆分为键值对数组（正则表达式 ";\\s*" 处理可能存在的空格）
        String[] keyValuePairs = cookie.split(";\\s*");

        for (String pair : keyValuePairs) {
            // 步骤2：按第一个等号拆分为key和value（避免值中包含等号）
            String[] keyValue = pair.split("=", 2);  // limit=2确保最多分割成两部分
            if (keyValue.length == 2) {
                String key = keyValue[0].trim();
                String value = keyValue[1].trim();
                orderedMap.put(key, value);
            }
        }
        return orderedMap;
    }

    public String sendPost(String name, String url,
                           Map<String, String> headers,
                           String jsonBody) throws IOException {
        try (CloseableHttpClient httpClient = HttpClients.createDefault()) {
            HttpPost httpPost = new HttpPost(url);
            // 添加自定义 Header
            if (headers != null) {
                for (Map.Entry<String, String> entry : headers.entrySet()) {
                    httpPost.setHeader(entry.getKey(), entry.getValue());
                }
            }
            log.info("【用户】：{}，【请求头】：{}，【请求体】：{}", name, JSON.toJSONString(headers), jsonBody);
            // 设置 JSON 请求体
            if (jsonBody != null) {
                httpPost.setEntity(new StringEntity(
                        jsonBody,
                        ContentType.APPLICATION_JSON
                ));
            }

            try (CloseableHttpResponse response = httpClient.execute(httpPost)) {
                HttpEntity entity = response.getEntity();
                Map<String, String> orderedMap = str2Map(CookieController.cookies.get(name).getValue());
                Header[] cookies = response.getHeaders("Set-Cookie");
                for (Header cookie : cookies) {
                    String[] keyValue = cookie.getValue().split("=", 2);
                    if (keyValue.length == 2) {
                        String key = keyValue[0].trim();
                        String value = keyValue[1].trim();
                        orderedMap.put(key, value);
                    }
                }
                String res = "";
                if (entity != null) {
                    res = EntityUtils.toString(entity);
                    Map<String, Object> result = (Map<String, Object>) JSON.parse(res);
                    int status = Integer.parseInt(result.get("status").toString());
                    if (status == 100) {
                        String stauthorization = result.get("data").toString();
                        orderedMap.put("Stauthorization", stauthorization);
                    }
                }
                String cookie_new = orderedMap.entrySet().stream()
                        .map(entry -> entry.getKey() + "=" + entry.getValue())
                        .collect(Collectors.joining("; "));
                if (courses.containsKey(name)) {
                    courses.get(name).setCookie(cookie_new);
                }
                CookieController.cookies.get(name).setValue(cookie_new);
                if (entity != null) {
                    return res;
                } else {
                    throw new IOException("Empty response");
                }
            }
        }
    }

    private String extractStudyScores(List<Map<String, Object>> study) {
        // 初始化分数变量
        String generalRequiredScore = "0";
        String industryRequiredScore = "0";
        String professionalCourseScore = "0";

        // 遍历study数组提取分数
        for (Map<String, Object> item : study) {
            String courseType = (String) item.get("coursetype");
            String score = item.get("s").toString();

            switch (courseType) {
                case "一般公需":
                    generalRequiredScore = score;
                    break;
                case "行业公需":
                    industryRequiredScore = score;
                    break;
                case "专业课程":
                    professionalCourseScore = score;
                    break;
            }
        }
        // 格式化输出
        return String.format("一般公需：%s分，行业公需：%s分，专业课程：%s分",
                generalRequiredScore, industryRequiredScore, professionalCourseScore);
    }
}
