#!/usr/bin/env python3
"""
S3 Data Download Script
Downloads data.csv from the aihacklondon S3 bucket
"""

import boto3
import pandas as pd
from botocore.exceptions import ClientError, NoCredentialsError
import os
import sys
from dotenv import load_dotenv
load_dotenv()  # This loads the .env file

# Your AWS Configuration
BUCKET_NAME = "aihac-1756568842"
FILE_KEY = "data.csv"
LOCAL_FILE_PATH = "data.csv"

def check_aws_credentials():
    """Check if AWS credentials are properly configured"""
    try:
        # Try to get caller identity to verify credentials
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"✅ AWS credentials verified for account: {identity['Account']}")
        print(f"   User/Role ARN: {identity['Arn']}")
        return True
    except NoCredentialsError:
        print("❌ No AWS credentials found!")
        print("Please configure credentials using one of these methods:")
        print("1. Run: aws configure")
        print("2. Set environment variables: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY")
        print("3. Use IAM role (if on EC2)")
        return False
    except Exception as e:
        print(f"❌ Error checking credentials: {e}")
        return False

def download_csv_file():
    """Download data.csv from S3 bucket"""
    try:
        # Create S3 client
        s3_client = boto3.client('s3')
        
        print(f"📥 Downloading {FILE_KEY} from s3://{BUCKET_NAME}...")
        
        # Check if bucket exists and we have access
        try:
            s3_client.head_bucket(Bucket=BUCKET_NAME)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                print(f"❌ Bucket '{BUCKET_NAME}' does not exist or you don't have access")
                return None
            elif error_code == '403':
                print(f"❌ Access denied to bucket '{BUCKET_NAME}'. Check your IAM permissions")
                return None
            else:
                print(f"❌ Error accessing bucket: {e}")
                return None
        
        # Check if file exists
        try:
            s3_client.head_object(Bucket=BUCKET_NAME, Key=FILE_KEY)
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                print(f"❌ File '{FILE_KEY}' not found in bucket '{BUCKET_NAME}'")
                print("Available files in bucket:")
                try:
                    response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, MaxKeys=10)
                    if 'Contents' in response:
                        for obj in response['Contents']:
                            print(f"   - {obj['Key']}")
                    else:
                        print("   (bucket is empty)")
                except Exception:
                    print("   (unable to list bucket contents)")
                return None
        
        # Download the file
        s3_client.download_file(BUCKET_NAME, FILE_KEY, LOCAL_FILE_PATH)
        
        # Get file size
        file_size = os.path.getsize(LOCAL_FILE_PATH)
        print(f"✅ File downloaded successfully!")
        print(f"   Local path: {LOCAL_FILE_PATH}")
        print(f"   File size: {file_size} bytes")
        
        return LOCAL_FILE_PATH
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'AccessDenied':
            print("❌ Access denied. Check your IAM permissions for S3DataAccessRole")
        else:
            print(f"❌ AWS error: {e}")
        return None
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

def load_csv_to_dataframe(file_path):
    """Load CSV file into pandas DataFrame"""
    try:
        print(f"📊 Loading {file_path} into pandas DataFrame...")
        df = pd.read_csv(file_path)
        
        print(f"✅ Data loaded successfully!")
        print(f"   Shape: {df.shape}")
        print(f"   Columns: {list(df.columns)}")
        
        # Display first few rows
        print("\n📋 First 5 rows:")
        print(df.head())
        
        # Basic info about the data
        print(f"\n📈 Data Info:")
        print(f"   Total rows: {len(df)}")
        print(f"   Total columns: {len(df.columns)}")
        print(f"   Memory usage: {df.memory_usage(deep=True).sum()} bytes")
        
        # Check for missing values
        missing_values = df.isnull().sum()
        if missing_values.any():
            print(f"\n⚠️  Missing values found:")
            for col, count in missing_values[missing_values > 0].items():
                print(f"   {col}: {count} missing")
        else:
            print("✅ No missing values found")
        
        return df
        
    except pd.errors.EmptyDataError:
        print("❌ The CSV file is empty")
        return None
    except pd.errors.ParserError as e:
        print(f"❌ Error parsing CSV: {e}")
        return None
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return None

def load_directly_from_s3():
    """Alternative method: Load CSV directly from S3 into memory without downloading"""
    try:
        s3_client = boto3.client('s3')
        
        print(f"📥 Loading {FILE_KEY} directly from S3 into memory...")
        
        # Get the object
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=FILE_KEY)
        
        # Read CSV directly into pandas
        df = pd.read_csv(response['Body'])
        
        print(f"✅ Data loaded directly from S3!")
        print(f"   Shape: {df.shape}")
        print(f"   Columns: {list(df.columns)}")
        
        return df
        
    except ClientError as e:
        print(f"❌ Error loading directly from S3: {e}")
        return None

def main():
    """Main function to orchestrate the download and loading process"""
    print("🚀 Starting S3 data download process...")
    print(f"Target: s3://{BUCKET_NAME}/{FILE_KEY}")
    print("-" * 50)
    
    # Check AWS credentials first
    if not check_aws_credentials():
        sys.exit(1)
    
    print("-" * 50)
    
    # Method 1: Download file then load
    print("📂 Method 1: Download file to disk then load")
    downloaded_file = download_csv_file()
    
    if downloaded_file:
        df = load_csv_to_dataframe(downloaded_file)
        
        if df is not None:
            print(f"\n🎉 Success! Your data is now available in the 'df' variable")
            
            # Optional: Clean up downloaded file
            cleanup = input("\n🗑️  Delete local file? (y/n): ").lower().strip()
            if cleanup in ['y', 'yes']:
                os.remove(LOCAL_FILE_PATH)
                print(f"✅ Cleaned up {LOCAL_FILE_PATH}")
            
            return df
    
    print("\n" + "-" * 50)
    
    # Method 2: Try direct loading as fallback
    print("📂 Method 2: Load directly from S3 (fallback)")
    df = load_directly_from_s3()
    
    if df is not None:
        print(f"\n🎉 Success! Your data is now available")
        return df
    else:
        print("❌ Both methods failed. Please check your AWS configuration.")
        return None

if __name__ == "__main__":
    # Run the script
    data = main()
    
    if data is not None:
        print("\n" + "="*50)
        print("📊 YOUR DATA IS READY!")
        print("="*50)
        print("The DataFrame is stored in the 'data' variable")
        print("You can now use it for analysis:")
        print("   - data.head() - view first 5 rows")
        print("   - data.info() - get column info")
        print("   - data.describe() - get statistics")
        print("   - data.shape - get dimensions")
        
        # Example usage
        print(f"\n📋 Quick preview:")
        print(data.head(3))
    else:
        print("\n❌ Failed to load data. Please check the error messages above.")
        sys.exit(1)