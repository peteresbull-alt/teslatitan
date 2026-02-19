from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_transaction_delete_payment'),
    ]

    operations = [
        # Clear existing rows before changing the schema (dev environment)
        migrations.RunSQL(
            "DELETE FROM app_customerpaymentinformation;",
            reverse_sql=migrations.RunSQL.noop,
        ),

        # Remove old fields
        migrations.RemoveField(model_name='customerpaymentinformation', name='payment_type'),
        migrations.RemoveField(model_name='customerpaymentinformation', name='payment_address'),

        # Change FK to add related_name
        migrations.AlterField(
            model_name='customerpaymentinformation',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='payment_methods',
                to='app.customuser',
            ),
        ),

        # Add new fields
        migrations.AddField(
            model_name='customerpaymentinformation',
            name='withdrawal_type',
            field=models.CharField(choices=[('BANK_WIRE', 'Bank Wire Transfer'), ('CRYPTO', 'Cryptocurrency')], max_length=100, default='CRYPTO'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='customerpaymentinformation',
            name='label',
            field=models.CharField(blank=True, help_text='Optional nickname for this payment method', max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='customerpaymentinformation',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='customerpaymentinformation',
            name='bank_name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='customerpaymentinformation',
            name='bank_account_name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='customerpaymentinformation',
            name='bank_account_number',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='customerpaymentinformation',
            name='routing_number',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='customerpaymentinformation',
            name='swift_code',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='customerpaymentinformation',
            name='bank_address',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customerpaymentinformation',
            name='crypto_address',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='customerpaymentinformation',
            name='crypto_type',
            field=models.CharField(
                blank=True,
                choices=[
                    ('BTC', 'Bitcoin (BTC)'), ('ETH', 'Ethereum (ETH)'), ('USDT', 'Tether (USDT)'),
                    ('USDC', 'USD Coin (USDC)'), ('BNB', 'BNB (BNB)'), ('SOL', 'Solana (SOL)'),
                    ('XRP', 'Ripple (XRP)'), ('LTC', 'Litecoin (LTC)'), ('DOGE', 'Dogecoin (DOGE)'),
                    ('TRX', 'TRON (TRX)'),
                ],
                max_length=100,
                null=True,
            ),
        ),
    ]
