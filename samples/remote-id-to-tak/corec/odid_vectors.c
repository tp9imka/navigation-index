/* Reference-vector harness for opendroneid-core-c (Apache-2.0).
 *
 *   odid_vectors gen <n> <seed>   encode random inputs with core-c, print hex + core-c decode
 *   odid_vectors fuzz <n> <seed>  random raw 25-byte messages, print hex + core-c decode
 *   odid_vectors decode           hex lines on stdin (message or pack), print core-c decode
 *
 * One JSON object per line. Floats are printed with %.17g so the Python side can compare
 * the exact float32/double values.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include "opendroneid.h"

static uint64_t rng_state;
static uint32_t rnd(void) {
    rng_state ^= rng_state << 13; rng_state ^= rng_state >> 7; rng_state ^= rng_state << 17;
    return (uint32_t) (rng_state >> 11);
}
static double urand(double lo, double hi) { return lo + (hi - lo) * (rnd() / 4294967295.0); }
static int irand(int lo, int hi) { return lo + (int) (rnd() % (uint32_t) (hi - lo + 1)); }

static void hex(const uint8_t *b, int n) { for (int i = 0; i < n; i++) printf("%02x", b[i]); }

static void rand_text(char *dst, int maxlen) {
    static const char cs[] = "ABCDEFGHJKLMNPQRSTUVWXYZ0123456789-_ ";
    int n = irand(0, maxlen);
    for (int i = 0; i < n; i++) dst[i] = cs[irand(0, (int) sizeof(cs) - 2)];
    dst[n] = 0;
}

static void dump_uas(const ODID_UAS_Data *u, int ret) {
    printf("\"ret\":%d", ret);
    for (int i = 0; i < ODID_BASIC_ID_MAX_MESSAGES; i++) {
        if (!u->BasicIDValid[i]) continue;
        printf(",\"BasicID%d\":{\"UAType\":%d,\"IDType\":%d,\"UASID\":\"", i, u->BasicID[i].UAType, u->BasicID[i].IDType);
        hex((const uint8_t *) u->BasicID[i].UASID, ODID_ID_SIZE);
        printf("\"}");
    }
    if (u->LocationValid) {
        const ODID_Location_data *l = &u->Location;
        printf(",\"Location\":{\"Status\":%d,\"Direction\":%.17g,\"SpeedHorizontal\":%.17g,\"SpeedVertical\":%.17g,"
               "\"Latitude\":%.17g,\"Longitude\":%.17g,\"AltitudeBaro\":%.17g,\"AltitudeGeo\":%.17g,\"HeightType\":%d,"
               "\"Height\":%.17g,\"HorizAccuracy\":%d,\"VertAccuracy\":%d,\"BaroAccuracy\":%d,\"SpeedAccuracy\":%d,"
               "\"TSAccuracy\":%d,\"TimeStamp\":%.17g}",
               l->Status, (double) l->Direction, (double) l->SpeedHorizontal, (double) l->SpeedVertical,
               l->Latitude, l->Longitude, (double) l->AltitudeBaro, (double) l->AltitudeGeo, l->HeightType,
               (double) l->Height, l->HorizAccuracy, l->VertAccuracy, l->BaroAccuracy, l->SpeedAccuracy,
               l->TSAccuracy, (double) l->TimeStamp);
    }
    for (int i = 0; i < ODID_AUTH_MAX_PAGES; i++) {
        if (!u->AuthValid[i]) continue;
        const ODID_Auth_data *a = &u->Auth[i];
        printf(",\"Auth%d\":{\"DataPage\":%d,\"AuthType\":%d,\"LastPageIndex\":%d,\"Length\":%d,\"Timestamp\":%u,\"AuthData\":\"",
               i, a->DataPage, a->AuthType, a->LastPageIndex, a->Length, a->Timestamp);
        hex(a->AuthData, ODID_AUTH_PAGE_NONZERO_DATA_SIZE);
        printf("\"}");
    }
    if (u->SelfIDValid) {
        printf(",\"SelfID\":{\"DescType\":%d,\"Desc\":\"", u->SelfID.DescType);
        hex((const uint8_t *) u->SelfID.Desc, ODID_STR_SIZE);
        printf("\"}");
    }
    if (u->SystemValid) {
        const ODID_System_data *s = &u->System;
        printf(",\"System\":{\"OperatorLocationType\":%d,\"ClassificationType\":%d,\"OperatorLatitude\":%.17g,"
               "\"OperatorLongitude\":%.17g,\"AreaCount\":%u,\"AreaRadius\":%u,\"AreaCeiling\":%.17g,\"AreaFloor\":%.17g,"
               "\"CategoryEU\":%d,\"ClassEU\":%d,\"OperatorAltitudeGeo\":%.17g,\"Timestamp\":%u}",
               s->OperatorLocationType, s->ClassificationType, s->OperatorLatitude, s->OperatorLongitude,
               s->AreaCount, s->AreaRadius, (double) s->AreaCeiling, (double) s->AreaFloor, s->CategoryEU,
               s->ClassEU, (double) s->OperatorAltitudeGeo, s->Timestamp);
    }
    if (u->OperatorIDValid) {
        printf(",\"OperatorID\":{\"OperatorIdType\":%d,\"OperatorId\":\"", u->OperatorID.OperatorIdType);
        hex((const uint8_t *) u->OperatorID.OperatorId, ODID_ID_SIZE);
        printf("\"}");
    }
}

static void emit(const uint8_t *buf, int len) {
    ODID_UAS_Data u;
    odid_initUasData(&u);
    int ret = (int) decodeOpenDroneID(&u, buf);
    printf("{\"hex\":\"");
    hex(buf, len);
    printf("\",");
    dump_uas(&u, ret);
    printf("}\n");
}

/* Mix of in-range values and edge cases (sentinels, clamps, rounding boundaries). */
static float pick(const float *edges, int n, double lo, double hi) {
    return irand(0, 3) == 0 ? edges[irand(0, n - 1)] : (float) urand(lo, hi);
}

static int gen_message(int type, ODID_Message_encoded *m) {
    memset(m, 0, sizeof(*m));
    switch (type) {
    case ODID_MESSAGETYPE_BASIC_ID: {
        ODID_BasicID_data d; odid_initBasicIDData(&d);
        d.IDType = irand(0, 4); d.UAType = irand(0, 15);
        if (d.IDType == ODID_IDTYPE_UTM_ASSIGNED_UUID || d.IDType == ODID_IDTYPE_SPECIFIC_SESSION_ID)
            for (int i = 0; i < ODID_ID_SIZE; i++) d.UASID[i] = (char) irand(0, 255);
        else
            rand_text(d.UASID, ODID_ID_SIZE);
        return encodeBasicIDMessage(&m->basicId, &d);
    }
    case ODID_MESSAGETYPE_LOCATION: {
        static const float dir_e[] = {0, 179.4f, 179.5f, 180, 359.4f, 359.6f, 360, 361};
        static const float sh_e[] = {0, 0.124f, 0.125f, 63.75f, 63.76f, 64.125f, 254.25f, 255};
        static const float sv_e[] = {-62, -0.25f, 0.25f, 0.75f, 62, 63};
        static const float alt_e[] = {-1000, -999.75f, 0, 0.25f, 31767.5f};
        static const float ts_e[] = {0, 0.05f, 0.15f, 3599.9f, 3600, 65535};
        ODID_Location_data d; odid_initLocationData(&d);
        d.Status = irand(0, 4); d.HeightType = irand(0, 1);
        d.Direction = pick(dir_e, 8, 0, 360);
        d.SpeedHorizontal = pick(sh_e, 8, 0, 254.25);
        d.SpeedVertical = pick(sv_e, 6, -62, 62);
        d.Latitude = irand(0, 9) == 0 ? 0.0 : urand(-90, 90);
        d.Longitude = irand(0, 9) == 0 ? 0.0 : urand(-180, 180);
        d.AltitudeBaro = pick(alt_e, 5, -1000, 31767.5);
        d.AltitudeGeo = pick(alt_e, 5, -1000, 31767.5);
        d.Height = pick(alt_e, 5, -1000, 31767.5);
        d.HorizAccuracy = irand(0, 12); d.VertAccuracy = irand(0, 6); d.BaroAccuracy = irand(0, 6);
        d.SpeedAccuracy = irand(0, 4); d.TSAccuracy = irand(0, 15);
        d.TimeStamp = pick(ts_e, 6, 0, 3600);
        return encodeLocationMessage(&m->location, &d);
    }
    case ODID_MESSAGETYPE_AUTH: {
        ODID_Auth_data d; odid_initAuthData(&d);
        d.DataPage = irand(0, 3); d.AuthType = irand(0, 5);
        if (d.DataPage == 0) { d.LastPageIndex = irand(0, 3); d.Length = irand(0, 17 + 23 * d.LastPageIndex); d.Timestamp = rnd(); }
        for (int i = 0; i < ODID_AUTH_PAGE_NONZERO_DATA_SIZE; i++) d.AuthData[i] = (uint8_t) irand(0, 255);
        if (d.DataPage == 0) memset(d.AuthData + ODID_AUTH_PAGE_ZERO_DATA_SIZE, 0, 6);
        return encodeAuthMessage(&m->auth, &d);
    }
    case ODID_MESSAGETYPE_SELF_ID: {
        ODID_SelfID_data d; odid_initSelfIDData(&d);
        d.DescType = irand(0, 2); rand_text(d.Desc, ODID_STR_SIZE);
        return encodeSelfIDMessage(&m->selfId, &d);
    }
    case ODID_MESSAGETYPE_SYSTEM: {
        static const float alt_e[] = {-1000, -999.75f, 0, 31767.5f};
        ODID_System_data d; odid_initSystemData(&d);
        d.OperatorLocationType = irand(0, 2); d.ClassificationType = irand(0, 1);
        d.OperatorLatitude = urand(-90, 90); d.OperatorLongitude = urand(-180, 180);
        d.AreaCount = (uint16_t) irand(0, 65535); d.AreaRadius = (uint16_t) irand(0, 2550);
        d.AreaCeiling = pick(alt_e, 4, -1000, 31767.5); d.AreaFloor = pick(alt_e, 4, -1000, 31767.5);
        d.CategoryEU = irand(0, 3); d.ClassEU = irand(0, 7);
        d.OperatorAltitudeGeo = pick(alt_e, 4, -1000, 31767.5);
        d.Timestamp = rnd();
        return encodeSystemMessage(&m->system, &d);
    }
    case ODID_MESSAGETYPE_OPERATOR_ID: {
        ODID_OperatorID_data d; odid_initOperatorIDData(&d);
        d.OperatorIdType = irand(0, 1) ? 0 : irand(0, 255);
        rand_text(d.OperatorId, ODID_ID_SIZE);
        return encodeOperatorIDMessage(&m->operatorId, &d);
    }
    }
    return ODID_FAIL;
}

static void gen(int n) {
    static const int types[] = {0, 1, 2, 3, 4, 5};
    for (int k = 0; k < n; k++) {
        if (k % 4 == 3) {
            ODID_MessagePack_data pd; odid_initMessagePackData(&pd);
            int want[] = {0, 1, 3, 4, 5, 2};
            int cnt = irand(1, 6);
            for (int i = 0; i < cnt; i++)
                if (gen_message(want[i], &pd.Messages[pd.MsgPackSize]) == ODID_SUCCESS) pd.MsgPackSize++;
            ODID_MessagePack_encoded pe; memset(&pe, 0, sizeof(pe));
            if (encodeMessagePack(&pe, &pd) != ODID_SUCCESS) continue;
            emit((const uint8_t *) &pe, 3 + ODID_MESSAGE_SIZE * pe.MsgPackSize);
        } else {
            ODID_Message_encoded m;
            if (gen_message(types[irand(0, 5)], &m) == ODID_SUCCESS)
                emit(m.rawData, ODID_MESSAGE_SIZE);
        }
    }
}

static void fuzz(int n) {
    static const uint8_t nibbles[] = {0, 1, 2, 3, 4, 5, 6, 9}; /* packs are covered by gen */
    for (int k = 0; k < n; k++) {
        uint8_t b[ODID_MESSAGE_SIZE];
        for (int i = 0; i < ODID_MESSAGE_SIZE; i++) b[i] = (uint8_t) irand(0, 255);
        uint8_t t = nibbles[irand(0, 7)];
        b[0] = (uint8_t) ((t << 4) | (b[0] & 0x0F));
        emit(b, ODID_MESSAGE_SIZE);
    }
}

static void decode_stdin(void) {
    char line[4096];
    while (fgets(line, sizeof(line), stdin)) {
        uint8_t buf[3 + ODID_MESSAGE_SIZE * ODID_PACK_MAX_MESSAGES];
        memset(buf, 0, sizeof(buf));
        int n = 0;
        for (char *p = line; p[0] && p[1] && n < (int) sizeof(buf); p += 2) {
            unsigned v;
            if (sscanf(p, "%2x", &v) != 1) break;
            buf[n++] = (uint8_t) v;
        }
        if (n >= ODID_MESSAGE_SIZE) emit(buf, n);
    }
}

int main(int argc, char **argv) {
    if (argc >= 2 && strcmp(argv[1], "decode") == 0) { decode_stdin(); return 0; }
    if (argc < 4) { fprintf(stderr, "usage: %s gen|fuzz <n> <seed> | decode\n", argv[0]); return 2; }
    rng_state = strtoull(argv[3], NULL, 10) * 2654435761ULL + 1;
    if (strcmp(argv[1], "gen") == 0) gen(atoi(argv[2]));
    else if (strcmp(argv[1], "fuzz") == 0) fuzz(atoi(argv[2]));
    else return 2;
    return 0;
}
