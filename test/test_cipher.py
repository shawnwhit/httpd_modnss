from test_config import Declarative
from test_util import run, assert_equal
import os
import nose
from nose.tools import make_decorator

# As of now there are 47 ciphers including ECC
WITH_ECC=47

cwd = os.getcwd()
srcdir = os.path.dirname(cwd)
exe = "%s/test_cipher" % srcdir
openssl = "/usr/bin/openssl"

ciphernum = 0

CIPHERS_NOT_IN_NSS = ['ECDH-RSA-AES128-SHA256',
                      'ECDH-ECDSA-AES128-GCM-SHA256',
                      'ECDH-ECDSA-AES128-SHA256',
                      'ECDH-RSA-AES128-GCM-SHA256',
                      'EXP-DES-CBC-SHA',
]

def assert_equal_openssl(nss_ciphers, ossl_ciphers):
    (nss, err, rc) = run([exe, "--o", nss_ciphers])
    assert rc == 0
    (ossl, err, rc) = run([openssl, "ciphers", ossl_ciphers])
    assert rc == 0

    nss_list = nss.strip().split(':')
    nss_list.sort()

    ossl_list = ossl.strip().split(':')
    ossl_list = list(set(ossl_list))
    ossl_list.sort()

    # NSS doesn't support the SHA-384 ciphers, remove them from the OpenSSL
    # output.
    t = list()
    for o in ossl_list:
        if 'SHA384' in o:
            continue
        if o in CIPHERS_NOT_IN_NSS:
            continue
        t.append(o)
    ossl_list = t

    if len(nss_list) > len(ossl_list):
        diff = set(nss_list) - set(ossl_list)
    elif len(ossl_list) > len(nss_list):
        diff = set(ossl_list) - set(nss_list)
    else:
        diff = ''

    assert nss_list == ossl_list, '%r != %r. Difference %r' % (':'.join(nss_list), ':'.join(ossl_list), diff)

class test_ciphers(object):
    @classmethod
    def setUpClass(cls):
        (out, err, rc) = run([exe, "--count"])
        assert rc == 0
        cls.ciphernum = int(out)

    def test_RSA(self):
        assert_equal_openssl("RSA", "RSA:-SSLv2:-SEED:-IDEA")

    def test_kRSA(self):
        assert_equal_openssl("kRSA", "kRSA:-SSLv2:-SEED:-IDEA")

    def test_aRSA(self):
        assert_equal_openssl("aRSA", "aRSA:-SSLv2:-SEED:-IDEA:-DH")

    def test_EDH(self):
        # No DH ciphers supported yet
        (out, err, rc) = run([exe, "EDH"])
        assert rc == 1

    def test_RC4(self):
        assert_equal_openssl("RC4", "RC4:-KRB5:-PSK:-ADH")

    def test_RC2(self):
        assert_equal_openssl("RC2", "RC2:-SSLv2:-KRB5")

    def test_AES(self):
        assert_equal_openssl("AES", "AES:-PSK:-ADH:-DSS:-DH")

    def test_AESGCM(self):
        assert_equal_openssl("AESGCM", "AESGCM:-PSK:-ADH:-DSS:-DH")

    def test_AES128(self):
        assert_equal_openssl("AES128", "AES128:-PSK:-ADH:-DSS:-DH")

    def test_AES256(self):
        assert_equal_openssl("AES256", "AES256:-PSK:-ADH:-DSS:-DH")

    def test_CAMELLIA(self):
        assert_equal_openssl("CAMELLIA", "CAMELLIA:-DH")

    def test_CAMELLIA128(self):
        assert_equal_openssl("CAMELLIA128", "CAMELLIA128:-DH")

    def test_CAMELLIA256(self):
        assert_equal_openssl("CAMELLIA256", "CAMELLIA256:-DH")

    def test_3DES(self):
        assert_equal_openssl("3DES", "3DES:-SSLv2:-PSK:-KRB5:-DH")

    def test_DES(self):
        assert_equal_openssl("DES", "DES:-SSLv2:-KRB5:-DH")

    def test_ALL(self):
        assert_equal_openssl("ALL", "ALL:-SSLv2:-KRB5:-ADH:-DH:-DSS:-PSK:-SEED:-IDEA")

    def test_ALL_no_AES(self):
        assert_equal_openssl("ALL:-AES", "ALL:-AES:-SSLv2:-KRB5:-ADH:-DH:-DSS:-PSK:-SEED:-IDEA")

    def test_COMPLEMENTOFALL(self):
        assert_equal_openssl("COMPLEMENTOFALL", "COMPLEMENTOFALL")

    # skipping DEFAULT as we use the NSS defaults
    # skipping COMPLEMENTOFDEFAULT as these are all ADH ciphers

    def test_SSLv3(self):
        assert_equal_openssl("SSLv3", "SSLv3:-KRB5:-PSK:-ADH:-EDH:-SEED:-IDEA")

    def test_SSLv3_equals_TLSv1(self):
        (nss, err, rc) = run([exe, "--o", "SSLv3"])
        (nss2, err, rc2) = run([exe, "--o", "TLSv1"])
        assert rc == 0
        assert rc2 == 0
        assert_equal(nss, nss2)

    def test_TLSv12(self):
        assert_equal_openssl("TLSv1.2", "TLSv1.2:TLSv1.2:-ADH:-DH:-DSS")

    def test_NULL(self):
        assert_equal_openssl("NULL", "NULL")

    def test_nss_rsa_rc4_128(self):
        # Test NSS cipher parsing
        (out, err, rc) = run([exe, "+rsa_rc4_128_md5,+rsa_rc4_128_sha"])
        assert rc == 0
        assert_equal(out, 'rsa_rc4_128_md5, rsa_rc4_128_sha')

    def test_EXP(self):
        assert_equal_openssl("EXP", "EXP:-SSLv2:-DH:-KRB5")

    def test_EXPORT(self):
        assert_equal_openssl("EXPORT", "EXPORT:-SSLv2:-DH:-KRB5")

    def test_EXPORT40(self):
        assert_equal_openssl("EXPORT40", "EXPORT40:-SSLv2:-ADH:-DH:-KRB5")

    def test_MD5(self):
        assert_equal_openssl("MD5", "MD5:-SSLv2:-DH:-KRB5")

    def test_SHA(self):
        assert_equal_openssl("SHA", "SHA:-SSLv2:-DH:-KRB5:-PSK:-IDEA:-SEED")

    def test_HIGH(self):
        assert_equal_openssl("HIGH", "HIGH:-SSLv2:-DH:-ADH:-KRB5:-PSK")

    def test_MEDIUM(self):
        assert_equal_openssl("MEDIUM", "MEDIUM:-SSLv2:-ADH:-KRB5:-PSK:-SEED:-IDEA")

    def test_LOW(self):
        assert_equal_openssl("LOW", "LOW:-SSLv2:-DH:-ADH:-KRB5")

    def test_SHA256(self):
        assert_equal_openssl("SHA256", "SHA256:-ADH:-DSS:-DH")

    def test_SHA_MD5_minus_AES(self):
        assert_equal_openssl("SHA:MD5:-AES", "SHA:MD5:-AES:-SSLv2:-DH:-DSS:-KRB5:-SEED:-PSK:-IDEA")

    def test_SHA_MD5_not_AES(self):
        assert_equal_openssl("!AES:SHA:MD5", "!AES:SHA:MD5:-SSLv2:-DH:-KRB5:-DSS:-SEED:-PSK:-IDEA")

    def test_aECDH(self):
        assert_equal_openssl("aECDH", "aECDH")

    def test_kECDHe(self):
        assert_equal_openssl("kECDHe", "kECDHe")

    def test_kECDHr(self):
        assert_equal_openssl("kECDHr", "kECDHr")

    def test_kEECDH(self):
        assert_equal_openssl("kEECDH", "kEECDH")

    def test_ECDH(self):
        assert_equal_openssl("ECDH", "ECDH")

    def test_AES_no_ECDH(self):
        assert_equal_openssl("AES:-ECDH", "AES:-ECDH:-ADH:-PSK:-DH")
        assert_equal_openssl("AES+RSA", "AES+RSA")

    def test_logical_and_3DES_RSA(self):
        assert_equal_openssl("3DES+RSA", "3DES+RSA:-SSLv2")

    def test_logical_and_RSA_RC4(self):
        assert_equal_openssl("RSA+RC4", "RSA+RC4:-SSLv2")

    def test_logical_and_ECDH_SHA(self):
        assert_equal_openssl("ECDH+SHA", "ECDH+SHA")

    def test_logical_and_RSA_RC4_no_SHA(self):
        assert_equal_openssl("RSA+RC4:!SHA", "RSA+RC4:-SSLv2:!SHA")

    def test_additive_RSA_RC4(self):
        assert_equal_openssl("RSA:+RC4", "RSA:+RC4:-SSLv2:-SEED:-IDEA")

    def test_negative_plus_RSA_MD5(self):
        assert_equal_openssl("-RC2:RSA+MD5", "-RC2:RSA+MD5:-SSLv2")

    def test_nss_subtraction(self):
        (out, err, rc) = run([exe, "+rsa_rc4_128_md5,+rsa_rc4_128_sha,-rsa_rc4_128_md5"])
        assert rc == 0
        assert_equal(out, 'rsa_rc4_128_sha')

    def test_openssl_cipher(self):
        (out, err, rc) = run([exe, "DES-CBC3-SHA"])
        assert rc == 0
        assert_equal(out, 'rsa_3des_sha')

    def test_openssl_cipherlist(self):
        (out, err, rc) = run([exe, "DES-CBC3-SHA:RC4-SHA"])
        assert rc == 0
        assert_equal(out, 'rsa_rc4_128_sha, rsa_3des_sha')

    # As long as at least one is valid, things are ok
    def test_nss_unknown(self):
        (out, err, rc) = run([exe, "+rsa_rc4_128_md5,+unknown"])
        assert rc == 0
        assert_equal(out, 'rsa_rc4_128_md5')

    def test_nss_single(self):
        (out, err, rc) = run([exe, "+aes_128_sha_256"])
        assert rc == 0
        assert_equal(out, 'aes_128_sha_256')

    def test_openssl_single_cipher(self):
        assert_equal_openssl("RC4-SHA", "RC4-SHA")

    def test_invalid_format(self):
        (out, err, rc) = run([exe, "none"])
        assert rc == 1
